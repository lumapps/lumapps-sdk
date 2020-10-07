# -*- coding: utf-8 -*-
from copy import deepcopy
from functools import lru_cache, partial
from io import FileIO
from json import dumps, loads
from logging import debug, exception, info, warning
from re import findall
from time import sleep, time
from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple

from httpx import HTTPStatusError, put
from slugify import slugify

from lumapps.api.base_client import BaseClient
from lumapps.api.decorators import (
    none_on_400_ALREADY_ARCHIVED,
    none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED,
    none_on_404,
    none_on_http_codes,
    raise_known_save_errors,
    retry_on_http_codes,
)
from lumapps.api.errors import (
    FileDownloadError,
    FileUploadError,
    FolderCreationError,
    GetTokenError,
    LumAppsClientConfError,
    MissingMetadataError,
    NonIdpGroupInCommunityError,
    get_http_err_content,
)
from lumapps.api.helpers import content_is_template, new_lumapps_uuid
from lumapps.api.utils import DiscoveryCacheDict

to_json = partial(dumps, indent=4)
RESERVED_SLUGS = frozenset(["news", "admin", "content", "registration"])
ApiClient = BaseClient


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


ApiClient = BaseClient  # pragma: no cover


class LumAppsClient(BaseClient):  # pragma: no cover
    def __init__(
        self,
        customer_id: str,
        instance_id: Optional[str],
        *args,
        cache: Optional[Any] = None,
        dry_run: bool = False,
        **kwargs,
    ):
        """ Create a LumAppsClient associated to a particular LumApps platform and site

            Args:
                customer_id: The id of the platform you target
                instance_id: The id of the instance you target
                args: The args to pass to the BaseClient
                cache: The cache to use
                dry_run: Whether to run in dry_run mode or not. This will
                    avoid saving things when callings save endpoints
                kwargs: The kwargs to pass to the BaseClient
        """
        if not customer_id:
            raise LumAppsClientConfError("customer_id required")
        self.customer_id = customer_id
        self.instance_id = instance_id
        if cache:
            self.cache = cache
        else:
            self.cache = DiscoveryCacheDict()
        self.dry_run = dry_run
        self._langs = None
        super().__init__(*args, **kwargs)
        self._cached_metadata = {}

    def _get_token_and_expiry(self, email: str) -> Tuple[str, int]:
        resp = self.get_call("user/getToken", customerId=self.customer_id, email=email)
        return resp["accessToken"], int(resp["expiresAt"])  # type: ignore

    def get_token_getter(self, email: str):
        assert email

        def f():
            k = f"{self.customer_id}|TOKEN|{email}"
            vals = self.cache.get(k)
            if vals:
                return vals
            try:
                token, expiry = self._get_token_and_expiry(email)
            except HTTPStatusError as err:
                if err.response.status_code == 403:
                    raise GetTokenError(get_http_err_content(err))
                raise
            self.cache.set(k, (token, expiry), int(expiry - time() - 180))
            return token, expiry

        return f

    def get_user_api(self, email: str, prune: bool = True) -> "LumAppsClient":
        return LumAppsClient(
            self.customer_id,
            self.instance_id,
            cache=self.cache,
            dry_run=self.dry_run,
            token_getter=self.get_token_getter(email),
            prune=prune,
            api_info=self.api_info,
            no_verify=self.no_verify,
            proxy_info=self.proxy_info,
        )

    @property  # type: ignore
    @lru_cache()
    def langs(self) -> List[str]:
        if self._langs:
            return self._langs
        k = f"{self.customer_id}|INSTANCE_LANGS|{self.instance_id}"
        langs = self.cache.get(k)
        if not langs:
            inst = self.get_instance()
            default_lang = inst.get("defaultLang")
            langs = [lang for lang in inst["langs"] if lang != default_lang]
            if default_lang:
                langs.insert(0, default_lang)
            self.cache.set(k, langs, 7200)
        return langs

    @property  # type: ignore
    @lru_cache()
    def first_lang(self) -> str:
        return self.langs[0]  # type: ignore

    def misc_urlinfo(self, url: str) -> Optional[Dict[str, Any]]:  # type: ignore
        """
        url: https://youtu.be/YPlnv2ovjw4#blabla?fooo
        Returns something looking like:
        {
            "url": "https://www.youtube.com/
                watch?v=YPlnv2ovjw4&feature=youtu.be",
            "images": ["https://i.ytimg.com/vi/YPlnv2ovjw4/maxresdefault.jpg"],
            "description": "Learn how to prepare for tsunamis: TsunamiZone.org",
            "title": "Staying Safe Where the Waves Break! - YouTube"
        }
        """
        return self.get_call("misc/urlinfo", url=url)  # type: ignore

    def get_available_instance_slug(self, desired_slug: str) -> str:
        """ Find an available instance slug according to
            the given slug and the current token customer.
            If the exact slug is not avaialble -i at the end until we
            found an available one or i reachs 300.

            Args:
                desired_slug: The desired slug

            Returns:
                The first available slug found

            Raises:
                Exception: Reached 300 try
        """
        post_fix = None
        while True:
            c = self.get_instance(slug=desired_slug, fields="id")
            if not c:
                return desired_slug
            if not post_fix:
                post_fix = 1
                desired_slug += "-1"
            else:
                desired_slug = desired_slug[: -len(str(post_fix)) - 1]
                post_fix += 1
                desired_slug += "-" + str(post_fix)
            if post_fix > 100:
                raise Exception("300 limit as slug postfix")

    def get_available_slug(self, desired_slug: str) -> str:
        """
            Find an available content slug according to
            the given slug and the current token customer.
            If the exact slug is not avaialble -i at the end until we
            found an available one or i reachs 300.

            Args:
                desired_slug: The desired slug

            Returns:
                The first available slug found

            Raises:
                Exception: Reached 300 try
        """
        post_fix = None
        while True:
            if desired_slug in RESERVED_SLUGS:
                c = True
            else:
                c = self.get_content_by_slug(desired_slug, fields="id")
            if not c:
                return desired_slug
            if not post_fix:
                post_fix = 1
                desired_slug += "-1"
            else:
                desired_slug = desired_slug[: -len(str(post_fix)) - 1]
                post_fix += 1
                desired_slug += "-" + str(post_fix)
            if post_fix > 300:
                raise Exception("300 limit as slug postfix")

    def get_available_slugs(self, titles: dict) -> Dict[str, str]:
        slugs = {lang: slugify(title) for lang, title in titles.items()}
        for lang, slug in slugs.items():
            slugs[lang] = self.get_available_slug(slug)
        return slugs

    @none_on_404
    def get_content(
        self,
        content_id: str,
        fields: str = None,
        action: str = "PAGE_EDIT",
        cache: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """ Get a content via his id

            Args:
                content_id: The id of the content to get
                fields: The fields projection to apply
                action: PAGE_EDIT
                cache: Whether to cache the result or not

            Returns:
                The retrieved content or None if it was not found
        """
        if cache:
            c = self.cache.get(f"{self.customer_id}|CONTENT|{content_id}")
            if c:
                return c
        params = {}
        if action:
            params["action"] = action
        if fields:
            params["fields"] = fields
        return self.get_call("content/get", uid=content_id, **params)  # type: ignore

    @none_on_404
    def get_content_by_slug(
        self, slug: str, fields: str = None, action: str = "PAGE_EDIT"
    ) -> Optional[Dict[str, Any]]:
        """
            Get a content via his slug

            Args:
                slug: The slug of the content to get
                fields: The fields projection to apply
                action: PAGE_EDIT

            Returns:
                The retrieved content or None if it was not found
        """
        params = {}
        if action:
            params["action"] = action
        if fields:
            params["fields"] = fields
        return self.get_call(
            "content/get", instance=self.instance_id, slug=slug, **params
        )  # type: ignore

    @lru_cache()
    def _get_template(self, template_id: str) -> Dict[str, Any]:
        return self.get_call("template/get", uid=template_id)  # type: ignore

    def get_template(self, template_id: str) -> Dict[str, Any]:
        return deepcopy(self._get_template(template_id))

    def iter_content_templates(
        self, content_type_id: str, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call(
            "template/list",
            instance=self.instance_id,
            customContentType=content_type_id,
            **kwargs,
        )  # type: ignore

    def iter_newsletters(self, **kwargs: dict) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call(
            "newsletter/list",
            instance=self.instance_id,
            customer=self.customer_id,
            **kwargs,
        )  # type: ignore

    def add_categories_to_community(
        self, community: dict, categories: list
    ) -> Optional[Dict[str, Any]]:
        c = community
        c.setdefault("tagsDetails", [])
        tags = c["tagsDetails"]
        lang = self.first_lang
        for tag in tags:
            tag_name = tag["name"][lang]
            if tag_name in categories:
                categories.remove(tag_name)
        if not categories:
            return c
        for cat in categories:
            tags.append(
                {
                    "$tempId": new_lumapps_uuid(),
                    "instance": community["instance"],
                    "kind": "community",
                    "name": {lang: cat},
                }
            )
        return None

    def get_community_category_ids(
        self, community: dict, categories: Sequence
    ) -> List[str]:
        lst = []
        categs = set(categories)
        for tag in community.get("tagsDetails", []):
            if tag["name"][self.first_lang] in categs:
                lst.append(tag["uid"])
        return lst

    def get_community_template(self, template_id: str) -> Dict[str, Any]:
        return self.get_call("communitytemplate/get", uid=template_id)  # type: ignore

    def iter_community_templates(
        self, **params
    ) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call(
            "communitytemplate/list", instanceId=self.instance_id, **params
        )

    def save_community_template(self, templ: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving community template: {to_json(templ)}")
        if self.dry_run:
            return templ
        return self.get_call("communitytemplate/save", body=templ)

    @none_on_404
    def get_community(
        self, community_id: str, fields: str = None
    ) -> Optional[Dict[str, Any]]:
        return self.get_call("community/get", uid=community_id, fields=fields)

    def iter_communities(self, **kwargs: dict) -> Generator[Dict[str, Any], None, None]:
        body = {"lang": "", "instanceId": self.instance_id}
        body.update(**kwargs)
        try:
            yield from self.iter_call("community/list", body=body)
        except HTTPStatusError as e:
            if e.response.status_code == 400 and "FEATURE_NOT_ENABLED" in str(e):
                return
            raise

    def iter_all_posts(
        self, **iter_posts_kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        for c in self.iter_communities(maxResults=100, fields="items(id)"):
            for p in self.iter_community_posts(c["id"], **iter_posts_kwargs):
                yield p

    def iter_contents(
        self, content_type_id: str = None, **kwargs
    ) -> Generator[Dict[str, Any], None, None]:
        """ Iterate over the contents on the current lumapps site \n

            https://apiv1.lumapps.com/#operation/Content/List

            Args:
                content_type_id: The id of a content type.
                    This will be used to filter the retrieved contents
                kwargs: The args to pass to the request (see lumapps api doc)

        """
        body = {"lang": "", "instanceId": self.instance_id, "action": "PAGE_EDIT"}
        if content_type_id:
            body["customContentType"] = content_type_id
        body.update(**kwargs)
        yield from self.iter_call("content/list", body=body)

    def iter_content_lists(
        self, content_type_id: str, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        body = {
            "customContentType": content_type_id,
            "customContentTypeTags": [],
            "instanceId": self.instance_id,
            "lang": self.first_lang,
            "type": "custom_list",
        }
        yield from self.iter_call("content/list", body=body, **kwargs)

    def get_news_content_type(self) -> Dict[str, Any]:
        for ct in self.iter_content_types():
            if ct["functionalInnerId"] == "news":
                return ct

    def get_page_content_type(self) -> Dict[str, Any]:
        for ct in self.iter_content_types():
            if ct["functionalInnerId"] == "page":
                return ct

    @none_on_404
    def get_content_type(self, content_type_id: str) -> Optional[Dict[str, Any]]:
        return self.get_call("customcontenttype/get", uid=content_type_id)

    def iter_content_types(
        self, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        args = {"instance": self.instance_id}
        args.update(**kwargs)
        yield from self.iter_call("customcontenttype/list", **args)

    def save_content_type(self, ct: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving content type: {to_json(ct)}")
        if self.dry_run:
            return ct
        return self.get_call("customcontenttype/save", body=ct)

    def iter_root_comments(
        self, content_id: str, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_comments(content_id, False, **kwargs)

    def iter_replies(
        self, content_id: str, parent: str, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_comments(content_id, False, parent=parent, **kwargs)

    def iter_comments(
        self, content_id: str, with_answers: bool = True, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call(
            "comment/list", content=content_id, withAnswers=with_answers, **kwargs
        )

    def mark_comment_as_relevant(self, comment_id: str) -> None:
        pl = {"uid": comment_id}
        info(f"Marking comment as relevant: {to_json(pl)}")
        if self.dry_run:
            return
        self.get_call("comment/markRelevant", body=pl)

    def hide_comment(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        if self.dry_run:
            return comment
        comment["status"] = "HIDE"
        return self.get_call("comment/save", body=comment, sendNotifications=False)

    @lru_cache()
    def get_content_slug_and_type(self, content_id: str) -> Tuple[str, str]:
        c = self.get_content(content_id, fields="slug,type", action=None)
        return (c["slug"], c["type"]) if c else ("", "")

    @none_on_404
    def get_post(self, post_id: str, **kwargs: dict) -> Optional[Dict[str, Any]]:
        return self.get_call("community/post/get", uid=post_id, **kwargs)

    @none_on_404
    def get_comment(
        self, comment_id: str, fields: str = None
    ) -> Optional[Dict[str, Any]]:
        return self.get_call("comment/get", uid=comment_id, fields=fields)

    @lru_cache()
    def get_user_url_path(self, user_email: str) -> Optional[str]:
        # https://foobar.com/home/ls/profile/5328742405898240
        inst_slug = self.get_instance_slug()
        u = self.get_user(user_email)
        if not u:
            return None
        user_id = u["id"]
        return f"/{inst_slug}/ls/profile/{user_id}"

    @lru_cache()
    def get_user_id_and_link_for_md(
        self, user_email: str
    ) -> Tuple[Optional[str], Optional[str]]:
        # @[john-doe:5286099950501888]
        u = self.get_user(user_email)
        if not u:
            return None, None
        user_id = u["id"]
        name_slug = slugify(u["fullName"])
        return f"@[{name_slug}:{user_id}]", user_id

    @lru_cache(maxsize=100000)
    def get_post_url_path(self, post_id: str, lang: str = None) -> str:
        post = self.get_post(post_id, fields="instance,externalKey")
        if not post:
            return ""
        assert post["instance"] == self.instance_id
        inst_slug = self.get_instance_slug()
        slug_dict = self.get_community_slug(post["externalKey"])
        slug = slug_dict[lang or self.first_lang]
        return f"/{inst_slug}/ls/community/{slug}/post/{post_id}"

    @lru_cache(maxsize=1000000)
    def get_content_url_path(self, content_id: str, lang: str = None) -> str:
        content = self.get_content(content_id, fields="instance,slug")
        if not content:
            return ""
        assert content["instance"] == self.instance_id
        inst_slug = self.get_instance_slug()
        content_slug = content["slug"][lang or self.first_lang]
        return f"/{inst_slug}/{content_slug}"

    @lru_cache()
    def get_comunity_url_path(self, community_id: str) -> Optional[str]:
        inst_slug = self.get_instance_slug()
        slug_dict = self.get_community_slug(community_id)
        if not slug_dict:
            return None
        return f"/{inst_slug}/ls/community/{slug_dict[self.first_lang]}"

    def iter_community_posts(
        self, community_id: str, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        for post in self.iter_posts(community_id, **kwargs):
            if post["externalKey"] == community_id:
                yield post

    def iter_posts(
        self, community_id: str = None, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        body = {"lang": "", "maxResults": 30}
        if community_id:
            body["contentId"] = [community_id]
        body.update(**kwargs)
        yield from self.iter_call("community/post/search", body=body)

    @lru_cache()
    @none_on_404
    def get_customer(self) -> Optional[Dict[str, Any]]:
        return self.get_call("customer/get", id=self.customer_id)

    @property
    def customer_slug(self) -> str:
        return self.get_customer()["slug"]

    @property
    @lru_cache()
    def domain_to_idp_dict(self) -> Dict[str, Any]:
        return {
            idp["domain"]: idp
            for idp in self.iter_call(
                "customer/identityprovider/list", customerId=self.customer_id
            )
            if idp.get("domain")
        }

    @lru_cache()
    def get_community_slug(self, community_id: str) -> Optional[str]:
        c = self.get_community(community_id)
        return c["slug"] if c else None

    @lru_cache()
    def get_instances(self) -> List[Dict[str, Any]]:
        lst = self.get_call("instance/list")
        return list(sorted(lst, key=lambda inst: inst.get("name", "")))

    @none_on_404
    def get_instance(
        self, *, slug: str = None, uid: str = None, **kwargs: dict
    ) -> Optional[Dict[str, Any]]:
        if slug:
            return self.get_call("instance/get", slug=slug, **kwargs)
        else:
            return self.get_call("instance/get", uid=uid or self.instance_id, **kwargs)

    @lru_cache()
    def get_instance_dict(self) -> Dict[str, Any]:
        return {inst["id"]: inst for inst in self.get_instances()}

    @lru_cache()
    def get_instance_slug(self) -> str:
        return self.get_instance_dict()[self.instance_id]["slug"]

    def get_user_settings(self) -> Dict[str, Any]:
        return self.get_call("user/settings/get")

    def save_user_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving user settings: {to_json(settings)}")
        if self.dry_run:
            return settings
        return self.get_call("user/settings/save", body=settings)

    def iter_users(self, **kwargs: dict) -> Generator[Dict[str, Any], None, None]:
        """ Iterate overs the platform users \n
            https://apiv1.lumapps.com/#operation/User/List

            Args:
                **kwargs: args to add to the request (see api documentation)

            Returns:
                A generator return the platform users
        """
        params = {"instance": self.instance_id}
        params.update(kwargs)
        yield from self.iter_call("user/list", **params)

    def iter_platform_users(
        self, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call("user/list", **kwargs)

    def save_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """ Save a user

            Args:
                user: The user to save

            Returns:
                The saved user
        """
        debug(f"Saving user: {to_json(user)}")
        if self.dry_run:
            return user
        return self.get_call("user/save", body=user)

    def iter_subscriptions(self) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call(
            "social/subscription/list", instanceKey=self.instance_id
        )

    @lru_cache()
    def get_user_forbidden_ok(self, id_or_email: str) -> Dict[str, Any]:
        k = f"{self.customer_id}|USER|{id_or_email}"
        try:
            return self.cache.get(k, raises=True)
        except KeyError:
            pass
        user = self._get_user_forbidden_ok(id_or_email)
        self.cache.set(k, user, 7200)
        return user

    @none_on_http_codes({403, 404})
    def _get_user_forbidden_ok(self, id_or_email: str) -> Optional[Dict[str, Any]]:
        assert id_or_email
        if "@" in id_or_email:
            return self.get_call("user/get", email=id_or_email)
        else:
            return self.get_call("user/get", uid=id_or_email)

    @lru_cache()
    def get_user(self, id_or_email: str) -> Dict[str, Any]:
        """ Get a user from his id or email

            Args:
                id_or_email: The id or email or the user

            Returns:
                The retrieved user
        """
        k = f"{self.customer_id}|USER|{id_or_email}"
        try:
            return self.cache.get(k, raises=True)
        except KeyError:
            pass
        user = self._get_user(id_or_email)
        self.cache.set(k, user, 7200)
        return user

    @none_on_404
    def _get_user(self, id_or_email: str) -> Optional[Dict[str, Any]]:
        assert id_or_email
        if "@" in id_or_email:
            return self.get_call("user/get", email=id_or_email)
        else:
            return self.get_call("user/get", uid=id_or_email)

    @lru_cache()
    def user_exists(self, email: str, is_active: bool = False) -> bool:
        user = self.get_user(email)
        if not user:
            return False
        return user.get("status") == "enabled" if is_active else True

    def iter_roles(self, **kwargs: dict) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call("role/list", instance=self.instance_id, **kwargs)

    def save_role(self, role: Dict[str, Any]) -> Dict[str, Any]:
        info(f"Saving role {to_json(role)}")
        if not self.dry_run:
            return self.get_call("role/save", body=role)

    def download_file(self, url: str, file_io: FileIO) -> Tuple[str, str]:
        """ Returns mime type from content-type header"""
        assert url
        try:
            with self.client.stream("GET", url) as r:
                r.raise_for_status()
                for chunk in r.iter_bytes():
                    if chunk:  # filter out keep-alive new chunks
                        file_io.write(chunk)
                if r.headers.get("Content-Disposition"):
                    fname = findall("filename=(.+)", r.headers["Content-Disposition"])[
                        0
                    ]
                    fname = fname.strip('"')
                else:
                    fname = url.strip("/").rpartition("/")[2]
                return fname, r.headers["content-type"]
        except Exception:
            exception(f"Failed to download file {url}:")
            raise FileDownloadError(url)

    def _get_upload_url(
        self, fname: str, folder_id: Optional[str], shared: bool
    ) -> Optional[str]:
        """ {
            "fileName": "orange.jpeg",
            "lang": "en",
            "parentPath":
                "provider=local/site=5763671289102336/resource=5718971551186944",
              or
            "parentPath": "provider=local/site=5763671289102336",
            "shared": true,
            "success": "/upload"
        } """
        parent_path = f"provider=local/site={self.instance_id}"
        if folder_id:
            parent_path += f"/resource={folder_id}"
        pl = {
            "fileName": fname,
            "lang": self.first_lang,
            "parentPath": parent_path,
            "shared": shared,
            "success": "/upload",
        }
        debug(f"Getting upload URL: {to_json(pl)}")
        if self.dry_run:
            return None
        upload_infos = self.get_call("document/uploadUrl/get", body=pl)
        return upload_infos["uploadUrl"]

    def _get_upload_url_sp(self, fname, drive_id, folder_id: Optional[str]):
        parent_path = f"provider=onedrive/drive={drive_id}"
        if folder_id:
            parent_path += f"/resource={folder_id}"
        pl = {
            "fileName": fname,
            "lang": self.first_lang,
            "parentPath": parent_path,
            "shared": False,
            "success": "/upload",
        }
        debug(f"Getting upload URL: {to_json(pl)}")
        if self.dry_run:
            return None
        upload_infos = self.get_call("document/uploadUrl/get", body=pl)
        return upload_infos["uploadUrl"]

    def _get_upload_url_google(self, fname, drive_id, folder_id: Optional[str]):
        if drive_id:
            parent_path = f"provider=drive/drive={drive_id}"
        else:
            parent_path = "provider=drive"
        if folder_id:
            parent_path += f"/resource={folder_id}"
        pl = {
            "fileName": fname,
            "lang": self.first_lang,
            "parentPath": parent_path,
            "shared": False,
            "success": "/upload",
        }
        debug(f"Getting upload URL: {to_json(pl)}")
        if self.dry_run:
            return None
        upload_infos = self.get_call("document/uploadUrl/get", body=pl)
        return upload_infos["uploadUrl"]

    def upload_personal_file(
        self, name: str, f: FileIO, folder_id: str, mime_type: str
    ) -> Optional[Dict[str, Any]]:
        return self.upload_file(name, f, folder_id, mime_type, False)

    def upload_instance_file(
        self, name: str, f: FileIO, folder_id: str, mime_type: str
    ) -> Optional[Dict[str, Any]]:
        return self.upload_file(name, f, folder_id, mime_type, True)

    def upload_file(
        self, name: str, f: FileIO, folder_id: str, mime_type: str, shared: bool
    ) -> Optional[Dict[str, Any]]:
        info(f"Uploading file {name}")
        if self.dry_run:
            return
        try:
            upload_url = self._get_upload_url(name, folder_id, shared)
        except HTTPStatusError as http_err:
            err_msg = get_http_err_content(http_err)
            warning(f"Error uploading {name}: {err_msg}")
            raise FileUploadError(err_msg)
        response = self.client.post(
            upload_url, files={"upload-file": (name, f, mime_type)}
        )
        try:
            response.raise_for_status()
        except HTTPStatusError as http_err:
            err_msg = get_http_err_content(http_err)
            warning(f"Error uploading {name}: {err_msg}")
            raise FileUploadError(err_msg)
        ret = response.json()
        if ret and ret.get("items"):
            return response.json()["items"][0]  # new "document" upload
        else:
            raise FileUploadError(
                f"No items returned after file upload, got: {to_json(ret)}"
            )

    def upload_file_to_sp(
        self, name: str, fh: FileIO, sp_drive_id: str, folder_id: str, fsize: int
    ) -> Optional[Dict[str, Any]]:
        info(f"Uploading file {name} to SharePoint")
        upload_url = self._get_upload_url_sp(name, sp_drive_id, folder_id)
        if self.dry_run:
            return
        pos = 0
        while True:
            chunk = fh.read(50_000_000)
            chunk_size = len(chunk)
            headers = {
                "Content-Length": str(fsize),
                "Content-Range": f"bytes {pos}-{pos + chunk_size - 1}/{fsize}",
            }
            try:
                resp = put(upload_url, data=chunk, headers=headers, timeout=120)
            except Exception as e:
                raise FileUploadError(e)
            if resp.status_code in (200, 201):
                return loads(resp.content.decode())
            if not (200 <= resp.status_code < 300):
                json_resp = resp.json()
                if json_resp:
                    raise FileUploadError(f"http code {resp.status_code}")
                else:
                    raise FileUploadError(f"http code {resp.status_code}\n{json_resp}")
            pos += chunk_size

    def upload_file_to_google(self, name, fh: FileIO, drive_id, folder_id, fsize):
        info(f"Uploading file {name} to Google Drive")
        upload_url = self._get_upload_url_google(name, drive_id, folder_id)
        # https://www.googleapis.com/upload/drive/v2/files/1...2L?uploadType=resumable&supportsAllDrives=true&upload_id=AB...EQ
        file_id = findall(r"https://.*/files/(.*)\?", upload_url)[0]
        if self.dry_run:
            return
        pos = 0
        while True:
            chunk = fh.read(52_428_800)  # 256 * 1024 * 200
            chunk_size = len(chunk)
            headers = {
                "Content-Length": str(chunk_size),
                "Content-Range": f"bytes {pos}-{pos + chunk_size - 1}/{fsize}",
            }
            try:
                resp = put(upload_url, data=chunk, headers=headers, timeout=120)
            except Exception as e:
                self.delete_document(f"provider=drive/resource={file_id}")
                raise FileUploadError(e)
            if resp.status_code in (200, 201):
                return loads(resp.content.decode())
            if not (200 <= resp.status_code < 300) and resp.status_code != 308:
                json_resp = resp.json()
                if json_resp:
                    raise FileUploadError(f"http code {resp.status_code}")
                else:
                    raise FileUploadError(f"http code {resp.status_code}\n{json_resp}")
            pos += chunk_size

    def upload_file_raw(
        self, name: str, f: FileIO, mime_type: str
    ) -> Optional[Dict[str, Any]]:
        info(f"Uploading file {name}")
        if self.dry_run:
            return
        # /upload, params ={"success": "/upload"}
        resp = self.client.get("/upload", params={"success": "/upload"})
        upload_url = resp.json()["uploadUrl"]
        response = self.client.post(
            upload_url, files={"upload-file": (name, f, mime_type)}
        )
        if response.status_code != 200:
            if response.status_code == 400:
                s = response.content.decode("utf-8")
                err = loads(s)
                err_msg = err.get("error", {}).get("message", "")
            else:
                err_msg = response.content.decode("utf-8")
            info(f"Error uploading {name}: {err_msg}")
            raise FileUploadError(err_msg)
        return response.json()

    def get_personal_folder(self, name: str) -> Optional[Dict[str, Any]]:
        return self.get_folder_by_name(name, False)

    def get_instance_folder(self, name: str) -> Optional[Dict[str, Any]]:
        return self.get_folder_by_name(name, True)

    def get_folder_by_name(self, name: str, shared: bool) -> Optional[Dict[str, Any]]:
        lang = self.first_lang
        for folder in self.iter_folders(lang, search_text=name, shared=shared):
            names = folder["name"]
            if name == names.get(lang) or list(names.values())[0]:
                return folder
        return None

    def create_or_get_personal_folder(self, name: str, author: str) -> Dict[str, Any]:
        return self.create_or_get_folder_by_name(name, False, author)

    def create_or_get_instance_folder(self, name: str) -> Dict[str, Any]:
        return self.create_or_get_folder_by_name(name, True)

    def create_or_get_folder_by_name(
        self, name: str, shared: bool, author: Optional[str] = None
    ) -> Dict[str, Any]:
        lang = self.first_lang
        from random import randint
        from time import sleep

        sleep(randint(0, 5))
        for folder in self.iter_folders(
            lang, search_text=name, shared=shared, author=author
        ):
            names = folder["name"]
            if name == names.get(lang) or list(names.values())[0]:
                return folder
        return self.save_folder(
            {
                "name": name,
                "parentPath": f"provider=local/site={self.instance_id}",
                "shared": shared,
            }
        )

    def create_folder(
        self, name: str, shared: bool, parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        folder = {
            "name": name,
            "parentPath": f"provider=local/site={self.instance_id}",
            "shared": shared,
        }
        if parent_id:
            folder["parentPath"] += f"/resource={parent_id}"
        try:
            return self.save_folder(folder)
        except HTTPStatusError as http_err:
            err_msg = get_http_err_content(http_err)
            warning(f"Error creating folder {name}: {err_msg}")
            raise FolderCreationError(err_msg)

    def save_folder(self, folder: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving folder: {to_json(folder)}")
        if self.dry_run:
            return folder
        return self.get_call("document/folder/save", body=folder)

    def update_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Updating document: {to_json(document)}")
        if self.dry_run:
            return document
        return self.get_call("document/update", body=document)

    def delete_document(self, doc_path):
        debug(f"Deleting document: {doc_path}")
        if self.dry_run:
            return
        body = {"docPath": doc_path}
        return self.get_call("document/trash", body=body)

    def iter_files(
        self, lang: Optional[str] = None, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_documents(
            lang or self.first_lang, incl_folders=False, **kwargs
        )

    def iter_folders(
        self, lang: Optional[str] = None, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_documents(
            lang or self.first_lang, incl_files=False, **kwargs
        )

    def iter_documents(
        self,
        lang: str,
        *,
        search_text: Optional[str] = None,
        author: Optional[str] = None,
        incl_folders: Optional[bool] = True,
        incl_files: Optional[bool] = True,
        folder_id: Optional[str] = None,
        shared: Optional[bool] = False,
        trashed: Optional[bool] = False,
        recursive: Optional[bool] = False,
    ) -> Generator[Dict[str, Any], None, None]:
        search_types = []
        if incl_folders:
            search_types.append("FOLDER")
        if incl_files:
            search_types.extend(["IMAGE", "OTHER"])
        doc_path = f"provider=local/site={self.instance_id}"
        if folder_id:
            doc_path += f"/resource={folder_id}"
        pl = {
            "lang": lang,
            "docPath": doc_path,
            "searchParameters": {
                "shared": shared,
                "trashed": trashed,
                "recursive": recursive,
            },
            "searchTypes": search_types,
            "maxResults": "100",
        }
        if search_text:
            pl["searchText"] = search_text
        if author:
            pl["searchParameters"]["author"] = author
        yield from self.iter_call("document/list", body=pl)

    def get_folder(self, folder_id: str) -> Dict[str, Any]:
        return self.get_document(folder_id)

    @none_on_http_codes({404})
    def get_document(self, id_: str) -> Optional[Dict[str, Any]]:
        """
        provider=local/site=5519565001981952/resource=5127875810951168
        """
        pl = {"docPath": f"provider=local/site={self.instance_id}/resource={id_}"}
        return self.get_call("document/get", body=pl)

    def iter_media_tags(self) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call("tag/list", instance=self.instance_id, kind="media")

    def save_media_tag(self, tag: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving media tag: {to_json(tag)}")
        if self.dry_run:
            return tag
        return self.get_call("tag/save", body=tag)

    def iter_global_widgets(self) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call("widget/list", instance=self.instance_id)

    def save_global_widget(self, widget: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving global widget: {to_json(widget)}")
        if self.dry_run:
            return widget
        return self.get_call("widget/save", body=widget)

    def get_media(self, media_id: str) -> Dict[str, Any]:
        """ prefer get_document above """
        return self.get_call("media/get", uid=media_id)

    def save_media(self, media: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving media: {to_json(media)}")
        if self.dry_run:
            return media
        return self.get_call("media/save", body=media)

    @none_on_http_codes({403, 404})
    def get_header(self, header_id: str) -> Optional[Dict[str, Any]]:
        return self.get_call("header/get", uid=header_id)

    def save_header(self, header: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving header: {to_json(header)}")
        if self.dry_run:
            return header
        return self.get_call("header/save", body=header)

    @none_on_http_codes({400, 404, 503})
    def get_style(self, style_id: str) -> Optional[Dict[str, Any]]:
        return self.get_call("style/get", uid=style_id)

    def save_style(self, style: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving style: {to_json(style)}")
        if self.dry_run:
            return style
        return self.get_call("style/save", body=style)

    def save_community_layout(self, community: Dict[str, Any]) -> Dict[str, Any]:
        if self.dry_run:
            return community
        return self.get_call("community/layout/save", body=community)

    def vote(self, post_id: str, vote_up: bool):
        if vote_up:
            vote = "up"
        else:
            vote = "down"
        if not self.dry_run:
            self.get_call("community/post/vote", uid=post_id, vote=vote)

    @none_on_http_codes({403})
    def share_post(
        self, post_id: str, target_community_ids: List[str]
    ) -> Optional[Dict[str, Any]]:
        if isinstance(target_community_ids, str):
            target_community_ids = [target_community_ids]
        pl = {
            "postId": post_id,
            "addToCommunities": target_community_ids,
        }
        if self.dry_run:
            return
        self.get_call("community/post/share", body=pl)

    @none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED
    def follow_content(self, content_id: str, notify: bool = True) -> Optional[Any]:
        if not self.dry_run:
            return self.get_call("content/follow", id=content_id, notify=notify)

    @none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED
    def follow_user(self, user_id: str) -> Optional[Any]:
        if not self.dry_run:
            return self.get_call("user/follow", id=user_id)

    def like_content(self, content_id: str):
        body = {"uid": content_id}
        debug(f"Liking content: {to_json(body)}")
        if not self.dry_run:
            return self.get_call("content/like", body=body, sendNotifications=False)

    def like_comment(self, comment_id: str):
        body = {"uid": comment_id}
        debug(f"Liking comment: {to_json(body)}")
        if not self.dry_run:
            return self.get_call("comment/like", body=body, sendNotifications=False)

    def iter_users_that_reacted(
        self, content_kind: str, content_id: str, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        """
        content_kind: page, custom, post, or comment
        """
        yield from self.iter_call(
            "user/list",
            action="PAGE_READ",
            instance=self.instance_id,
            lang=self.first_lang,
            reactedEntityKey=content_id,
            reactedEntityKind=content_kind,
            showHidden=False,
            status="enabled",
            **kwargs,
        )

    @none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED
    def pin_post(self, community_id: str, post_id: str) -> Optional[Dict[str, Any]]:
        if self.dry_run:
            return
        pl = {"communityId": community_id, "uid": post_id}
        return self.get_call("community/post/pin", body=pl)

    def iter_nav_element_ids(self, lang: str) -> Generator[Dict[str, Any], None, None]:
        for content in self.iter_call(
            "content/list",
            customerId=self.customer_id,
            instanceId=self.instance_id,
            lang=lang,
            type=["menu"],
            fields="items(id)",
        ):
            yield content["id"]

    def get_menu(
        self, lang: Optional[str] = None, action: str = "MENU_EDIT"
    ) -> Sequence[dict]:
        lang = lang or self.first_lang
        resp = self.get_call(
            "content/menu/get",
            action=action,
            customer=self.customer_id,
            instance=self.instance_id,
            lang=lang,
        )
        return resp if isinstance(resp, list) else []

    def save_menu(self, lang: str, menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        body = {
            "instanceId": self.instance_id,
            "deleted": [],
            "customerId": self.customer_id,
            "items": {"lang": lang, "items": menu_items},
        }
        debug(f"Saving menu: {to_json(body)}")
        if self.dry_run:
            return body
        return self.get_call("content/menu/save", body=body)

    def delete_content(self, content_id: str) -> None:
        debug(f"Deleting content: {content_id}")
        if not self.dry_run:
            self.get_call("content/delete", uid=content_id)

    def delete_post(self, post_id: str) -> None:
        debug(f"Deleting post: {post_id}")
        if not self.dry_run:
            self.get_call("community/post/delete", uid=post_id)

    def delete_community(self, community_id: str) -> None:
        debug(f"Deleting community: {community_id}")
        if not self.dry_run:
            self.get_call("community/delete", uid=community_id)

    def unarchive_content(self, content: Dict[str, Any]):
        debug(f"Unarchiving content: {to_json(content)}")
        if self.dry_run:
            return content
        return self.get_call("content/unarchive", body=content)

    @none_on_400_ALREADY_ARCHIVED
    def archive_content(self, content: Dict[str, Any]) -> Optional[Any]:
        debug(f"Archiving content: {to_json(content)}")
        if self.dry_run:
            return content
        if content_is_template(content):
            raise Exception("cannot archive a template")
        return self.get_call("content/archive", body=content)

    def save_widget(self, widget: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving widget: {to_json(widget)}")
        if self.dry_run:
            return widget
        return self.get_call("widget/save", body=widget)

    def save_instance(self, instance: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving instance: {to_json(instance)}")
        if self.dry_run:
            return instance
        return self.get_call("instance/save", body=instance)

    def save_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving template: {to_json(template)}")
        if self.dry_run:
            return template
        assert content_is_template(template)
        return self.get_call("template/save", body=template)

    @none_on_http_codes({503})
    def save_menu_content(self, content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        debug(f"Saving menu content: {to_json(content)}")
        if self.dry_run:
            return content
        assert content.get("type") == "menu"
        return self.get_call("content/save", body=content, sendNotifications=False)

    @raise_known_save_errors
    def save_content(
        self, content: Dict[str, Any], cache: bool = False
    ) -> Dict[str, Any]:
        """ Save a content

            Args:
                content: The content to save
                cache: Whether to cache the saved content based on his id

            Returns:
                The saved content
        """
        debug(f"Saving content: {to_json(content)}")
        if self.dry_run:
            return content
        assert not content_is_template(content)
        dst = self.get_call("content/save", body=content, sendNotifications=False)
        if cache:
            self.cache.set(f"{self.customer_id}|CONTENT|{dst['id']}", dst, 5 * 60 * 60)
        return dst

    def set_homepage(self, content_id: str) -> None:
        debug(f"Setting content {content_id} as home page")
        if self.dry_run:
            return
        self.get_call("content/setHomepage", body={"uid": content_id})

    def re_save_post(self, post_id: str) -> None:
        try:
            info(f"doing re_save_post for {post_id}")
            post = self.get_post(post_id)
            if not post:
                info(f"post {post_id} not found")
                return
            post.pop("authorDetails", None)
            post.pop("visibleInCommunitiesDetails", None)
            self.save_post(post)
            info(f"re_save_post done for {post_id}")
        except Exception:
            exception("re_save_post failed:")

    def save_post(self, post: Dict[str, Any], cache: bool = False) -> Dict[str, Any]:
        debug(f"Saving post: {to_json(post)}")
        if self.dry_run:
            return post
        try:
            dst = self.get_call(
                "community/post/save", body=post, sendNotifications=False
            )
        except HTTPStatusError as e:
            if e.response.status_code == 400 and "CONTENT_NOT_UP_TO_DATE" in str(e):
                dst = self.get_call(
                    "community/post/save", body=post, sendNotifications=False
                )
            else:
                exception("Error saving post:")
                raise
        if cache:
            self.cache.set(f"{self.customer_id}|POST|{dst['id']}", dst, 5 * 60 * 60)
        return dst

    @none_on_404
    def get_community_by_slug(self, slug: str) -> Dict[str, Any]:
        return self.get_call("community/get", instance=self.instance_id, slug=slug)

    @lru_cache()
    def get_all_group_id(self) -> str:
        k = f"{self.customer_id}|GROUP_ALL_ID"
        group_id = self.cache.get(k)
        if group_id:
            return group_id
        body = {
            "customerId": self.customer_id,
            "query": "all",
            "hasGroup": False,
            "fields": "items(id,functionalInnerId)",
        }
        attempts = 0
        while attempts < 3:
            attempts += 1
            for i, g in enumerate(self.iter_call("feed/search", body=body)):
                if g["functionalInnerId"] == "LUMAPPS_ALL":
                    self.cache.set(k, g["id"], 7200)
                    return g["id"]
        raise Exception("Cannot find ALL group")

    @lru_cache()
    def get_public_group_id(self, missing_ok: bool = False) -> Optional[str]:
        k = f"{self.customer_id}|GROUP_PUBLIC_ID"
        try:
            return self.cache.get(k, raises=True)
        except KeyError:
            pass
        body = {
            "customerId": self.customer_id,
            "query": "public",
            "hasGroup": False,
            "fields": "items(id,functionalInnerId)",
        }
        attempts = 0
        while attempts < 3:
            attempts += 1
            for i, g in enumerate(self.iter_call("feed/search", body=body)):
                if g["functionalInnerId"] == "LUMAPPS_PUBLIC":
                    self.cache.set(k, g["id"], 7200)
                    return g["id"]
        if not missing_ok:
            raise Exception("Cannot find PUBLIC group")
        else:
            self.cache.set(k, None, 7200)
            return None

    @lru_cache()
    def get_group(self, group_id: str) -> Dict[str, Any]:
        """ Get a group by his id

            Args:
                group_id: The id of the group

            Returns:
                The retrieved group
        """
        return self.get_call("feed/get", uid=group_id)

    @lru_cache()
    @none_on_http_codes({403})
    def get_group_forbidden_ok(self, group_id: str) -> Optional[Dict[str, Any]]:
        return self.get_call("feed/get", uid=group_id)

    def save_community(
        self, community: Dict[str, Any], notuptodate_ok: bool = False
    ) -> Dict[str, Any]:
        debug(f"Saving community: {to_json(community)}")
        if self.dry_run:
            return community
        try:
            return self.get_call("community/save", body=community)
        except HTTPStatusError as e:
            if e.response.status_code != 400:
                raise
            content = get_http_err_content(e)
            if "FEED_GOOGLE_OR_MICROSOFT_GROUP_ONLY" in content:
                raise NonIdpGroupInCommunityError("Community has non-IDP feeds")
            if "CONTENT_NOT_UP_TO_DATE" in content and notuptodate_ok:
                assert community["instance"] == self.instance_id
                return self.get_community_by_slug(community["slug"][self.first_lang])
            raise

    def iter_root_metadata(
        self, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        args = {
            "customerId": self.customer_id,
            "instance": self.instance_id,
            "emptyParent": True,
            "lang": self.first_lang,
        }
        args.update(**kwargs)
        yield from self.iter_call("metadata/list", **args)

    def iter_metadata(
        self, family_id: str, parent_id: str, **kwargs: dict
    ) -> Generator[Dict[str, Any], None, None]:
        args = {
            "customerId": self.customer_id,
            "customer": self.customer_id,
            "instance": self.instance_id,
            "parent": parent_id,
            "familyId": family_id,
            "lang": self.first_lang,
        }
        args.update(**kwargs)
        for md in self.iter_call("metadata/list", **args):
            cache_key = (md["familyKey"], md.get("parent"), dumps(md["name"]))
            self._cached_metadata[cache_key] = md
            yield md

    def get_or_add_metadata(self, new_md: dict) -> Dict[str, Any]:
        name = new_md["name"]
        family_id = new_md["familyKey"]
        parent_id = new_md["parent"]
        cache_key = (family_id, parent_id, dumps(name))
        if cache_key in self._cached_metadata:
            return self._cached_metadata[cache_key]
        for metadata in self.iter_metadata(family_id, parent_id):
            assert metadata.get("parent") == parent_id
            if metadata["name"] == name:
                return metadata
        return self.save_metadata(new_md)

    @lru_cache()
    def get_metadata_by_name(
        self, name: str, parent_id: str = None, create: bool = False
    ) -> Dict[str, Any]:
        inst_id = self.instance_id
        metadatas = self.get_call(
            "metadata/list", instance=inst_id, parent=parent_id, familyId=parent_id
        )
        for metadata in metadatas:
            md_names = list(v.lower() for v in metadata["name"].values())
            if name.lower() in md_names:
                if metadata.get("parent") == parent_id:
                    return metadata
        if not create:
            raise MissingMetadataError(
                f"Metadata {name} with parent {parent_id} not found"
            )
        return self.add_metadata(name, parent_id)

    @lru_cache()
    def get_metadata(self, metadata_id: str) -> Dict[str, Any]:
        return self.get_call("metadata/get", uid=metadata_id)

    @lru_cache()
    @none_on_http_codes({403})
    def get_metadata_forbidden_ok(
        self, metadata_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        return self.get_call("metadata/get", uid=metadata_id)

    def add_metadata(self, name: str, parent_id: str = None) -> Dict[str, Any]:
        if not parent_id:
            raise Exception("will not create a metadata without a parent")
        inst_id = self.instance_id
        metadatas = self.get_call(
            "metadata/list", instance=inst_id, parent=parent_id, familyId=parent_id
        )
        for metadata in metadatas:
            if metadata["name"].get(self.first_lang) == name:
                if metadata.get("parent") == parent_id:
                    return metadata
        metadata = {
            "customer": self.customer_id,
            "displayInFilter": False,
            "familyKey": parent_id,
            "heritable": False,
            "instance": inst_id,
            "isVisibleFront": False,
            "multiple": False,
            "name": {self.first_lang: name},
            "parent": parent_id,
            # "sortOrder": "0",
        }
        if self.dry_run:
            return metadata
        return self.save_metadata(metadata)

    def save_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving metadata: {to_json(metadata)}")
        if int(metadata.get("sortOrder", 0)) < 0:
            metadata.pop("sortOrder")
        if self.dry_run:
            return metadata
        return self.get_call("metadata/save", body=metadata)

    def save_comment(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving comment: {to_json(comment)}")
        if self.dry_run:
            return comment
        while True:
            try:
                return self.get_call(
                    "comment/save", body=comment, sendNotifications=False
                )
            except HTTPStatusError as err:
                if err.response.status_code == 400:
                    if "RATE_LIMIT_EXCEEDED" in err._get_reason():
                        warning("RATE_LIMIT_EXCEEDED, sleeping 61 seconds")
                        sleep(61)
                        continue
                raise

    @lru_cache()
    def get_cached_groups(self) -> List[Dict[str, Any]]:
        return self.get_call("feed/list", instance=self.instance_id)

    @lru_cache()
    def get_cached_group_id_by_name(
        self, name: str, feed_type_id: str = None
    ) -> Optional[Dict[str, Any]]:
        body = {"instance": self.instance_id, "query": name}
        if feed_type_id:
            body["type"] = feed_type_id
        groups = self.get_call("feed/search", body=body)
        for group in groups:
            if group["name"].lower() != name.lower():
                continue
            if feed_type_id and group["type"] != feed_type_id:
                continue
            return group
        return None

    @lru_cache()
    def get_cached_groups_dict_by_name(self) -> Dict[str, Any]:
        groups = self.get_cached_groups()
        return {g["name"].lower(): g for g in groups}

    def add_user_to_group(self, feed_id: str, user_email: str):
        body = {"addedUsers": [user_email], "feed": feed_id, "removedUsers": []}
        if self.dry_run:
            return body
        return self.get_call("feed/subscribers/save", body=body)

    @retry_on_http_codes({503})
    def add_users_to_group(
        self, feed_id: str, user_emails: List[str]
    ) -> Optional[Dict[str, Any]]:
        body = {"addedUsers": user_emails, "feed": feed_id, "removedUsers": []}
        debug(f"Adding users to group: {to_json(body)}")
        if self.dry_run:
            return body
        return self.get_call("feed/subscribers/save", body=body)

    def add_users_to_group_skip_missing(
        self, feed_id: str, user_emails: List[str]
    ) -> List[str]:
        missing = []
        for chunk in chunks(user_emails, 5):
            to_add = chunk
            while True:
                try:
                    self.add_users_to_group(feed_id, to_add)
                    break
                except HTTPStatusError as e:
                    resp = e.response
                    if resp.status_code != 404:
                        exception("error adding users:")
                        raise
                    msg = loads(resp.content.decode())["error"]["errors"][0]["message"]
                    # 'User not found: foo.bar@acme.org'
                    member = msg.split(": ")[1]
                    warning(f"Failed to add missing {member} to group {feed_id}")
                    missing.append(member)
                    to_add = chunk[chunk.index(member) + 1 :]
        return missing

    def delete_instance(self):
        if self.dry_run:
            return
        if False:
            self.get_call("instance/delete", uid="dangerous stuff")

    def get_instance_group_type_for_name(self, name: str) -> str:
        name = name.lower()
        for group_type in self.iter_instance_group_types():
            if not group_type.get("instance"):
                continue
            if group_type["name"].lower() == name:
                return group_type["id"]

    def iter_groups(self, type_id: str) -> Generator[Dict[str, Any], None, None]:
        """ Iter the groups on the current site

            Args:
                type_id: The id of the group type (feedType or category) to filter on

            Returns:
                The groups in that group type
        """
        return self.iter_call(
            "feed/list", instance=self.instance_id, type=type_id, action="GROUP_EDIT"
        )

    def iter_platform_group_types(self) -> Generator[Dict[str, Any], None, None]:
        """ Iterate over the platform group types

            Yield:
                A group
        """
        for gt in self.iter_call("feedtype/list", customer=self.customer_id):
            if not gt.get("instance"):
                yield gt

    def iter_instance_group_types(self) -> Generator[Dict[str, Any], None, None]:
        """ Iterate over the site group types
        """
        for gt in self.iter_call(
            "feedtype/list", customer=self.customer_id, instance=self.instance_id
        ):
            if gt.get("instance"):
                yield gt

    def save_group_type(self, group_type: Dict[str, Any]) -> Dict[str, Any]:
        info(f"Saving group type: {to_json(group_type)}")
        if self.dry_run:
            return group_type
        return self.get_call("feedtype/save", body=group_type)

    def delete_group(self, group_id: str) -> None:
        info(f"Deleting group {group_id}")
        if self.dry_run:
            return
        self.get_call("feed/delete", uid=group_id)

    def save_group(self, group: Dict[str, Any], retries: int = 0) -> Dict[str, Any]:
        """ Save a group

            Args:
                group: The group to save
                retries: The number of retries on failure to do

            Returns:
                The saved group
        """
        info(f"Saving group: {to_json(group)}")
        if self.dry_run:
            return group
        attempt = 0
        while True:
            attempt += 1
            try:
                return self.get_call("feed/save", body=group)
            except HTTPStatusError as e:
                if e.response.status_code == 503 and attempt < 1 + retries:
                    sleep_time = (attempt + 1) * 3
                    warning(f"503 saving the feed, will retry in {sleep_time}s")
                    sleep(sleep_time)
                    continue
                raise

    def add_global_group(
        self, grouptype_id: str, name: str, *, google_group_email: str = None
    ) -> Dict[str, Any]:
        return self._add_group(grouptype_id, name, google_group_email, True)

    def add_local_group(
        self, grouptype_id: str, name: str, *, google_group_email: str = None
    ) -> Dict[str, Any]:
        return self._add_group(grouptype_id, name, google_group_email, False)

    def _add_group(
        self, grouptype_id: str, name: str, google_group_email: str, global_group: bool
    ) -> Dict[str, Any]:
        info(f"Adding {'global' if global_group else 'instance'} group {name}")
        group = {
            "customer": self.customer_id,
            "functionalInnerId": slugify(name),  # code
            "heritable": True,
            "name": name,
            "status": "enabled",
            "type": grouptype_id,
        }
        if google_group_email:
            group["group"] = google_group_email
        if not global_group:
            group["instance"] = self.instance_id
        info(f"Saving group {to_json(group)}")
        if self.dry_run:
            return group
        group = self.get_call("feed/save", body=group)
        self.get_cached_groups.cache_clear()
        self.get_cached_group_id_by_name.cache_clear()
        self.get_cached_groups_dict_by_name.cache_clear()
        return group

    def sync_group(self, group_id: str):
        if self.dry_run:
            return
        self.get_call("feed/synchronize", body={"uid": group_id})

    def iter_instance_admins(self) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call("instance/admin/list", uid=self.instance_id)

    def iter_customer_admins(self) -> Generator[Dict[str, Any], None, None]:
        yield from self.iter_call("customer/admin/list", uid=self.instance_id)

    @none_on_http_codes({404, 503})
    def add_instance_admin(self, email: str) -> Optional[bool]:
        if self.dry_run:
            return
        self.get_call("instance/admin/add", uid=self.instance_id, email=email)
        return True

    @none_on_http_codes({400, 404})
    def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        return self.get_call("workspace/get", workspaceId=workspace_id)

    def iter_modules(self, **kwargs: dict) -> Generator[Dict[str, Any], None, None]:
        pl = {
            "customerId": self.customer_id,
            "instanceId": self.instance_id,
            "lang": self.first_lang,
            "action": "CUSTOM_EDIT",
            "excludeType": [
                "community",
                "custom",
                "custom_list",
                "image_gallery",
                "menu",
                "news",
                "news_list",
                "page",
                "post",
            ],
            "type": ["directory", "user_directory", "tutorial"],
        }
        pl.update(**kwargs)
        yield from self.iter_call("content/list", body=pl)

    @none_on_http_codes({404})
    def get_directory(self, uid: str) -> Optional[Dict[str, Any]]:
        return self.get_call("directory/get", uid=uid)

    def save_directory(self, directory: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving directory: {to_json(directory)}")
        if self.dry_run:
            return directory
        return self.get_call("directory/save", body=directory)

    def iter_directory_entries(
        self, directory_id: str
    ) -> Generator[Dict[str, Any], None, None]:
        pl = {
            "lang": self.first_lang,
            "directory": directory_id,
            "displaySortMandatory": False,
            "includeUserEntries": False,
        }
        yield from self.iter_call("directory/entry/list", body=pl)

    def iter_personal_directory_entries(
        self, directory_id: str, non_personal_ids: Sequence[str]
    ) -> Generator[Dict[str, Any], None, None]:
        pl = {
            "lang": self.first_lang,
            "directory": directory_id,
            "displaySortMandatory": False,
            "includeUserEntries": True,
        }
        for dir_entry in self.iter_call("directory/entry/list", body=pl):
            if dir_entry["id"] not in non_personal_ids:
                yield dir_entry

    def save_directory_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving directory entry: {to_json(entry)}")
        if self.dry_run:
            return entry
        return self.get_call("directory/entry/save", body=entry)

    def save_personal_directory_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving personal directory entry: {to_json(entry)}")
        if self.dry_run:
            return entry
        return self.get_call("directory/entry/user/save", body=entry)

    @none_on_http_codes({404})
    def get_directory_entry(self, uid: str) -> Optional[Dict[str, Any]]:
        return self.get_call("directory/entry/get", uid=uid)

    def mark_directory_entry_favorite(self, dir_entry_uid: str):
        debug(f"Marking directory entry {dir_entry_uid} favorite")
        pl = {"target": {"kind": "DirectoryEntry", "uid": dir_entry_uid}}
        if self.dry_run:
            return
        return self.get_call("favorite/mark_as_favorite", body=pl)

    @none_on_http_codes({404})
    def get_tutorial(self, uid: str) -> Optional[Dict[str, Any]]:
        return self.get_call("tutorial/get", uid=uid)

    @none_on_http_codes({404})
    def get_newsletter(self, uid: str) -> Optional[Dict[str, Any]]:
        return self.get_call("newsletter/get", uid=uid)

    def save_tutorial(self, tutorial: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving tutorial: {to_json(tutorial)}")
        if self.dry_run:
            return tutorial
        return self.get_call("tutorial/save", body=tutorial)

    def save_newsletter(self, newsletter: Dict[str, Any]) -> Dict[str, Any]:
        debug(f"Saving newsletter: {to_json(newsletter)}")
        if self.dry_run:
            return newsletter
        return self.get_call("newsletter/save", body=newsletter)

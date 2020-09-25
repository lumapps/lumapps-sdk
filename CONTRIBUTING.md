# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## Environment setup

First install dependencies and setup pre-commits hooks

```bash
make setup
```

You can run `make help` to see all available actions !

### Adding a new dependency

To add a dependency use poetry

```bash
poetry add <dependency>
```

## Dev

### Code

First open an issue to discuss the matter before coding.
When your idea has been approved, create a new branch `git checkout -b <new_branch_name>` and open a Pull Request.

Before commiting you can run tests and type checks via the commands

```bash
make check
make test
```

## Commits format

Commits format is enforced according to the tool https://github.com/lumapps/commit-message-validator

A pre-commit hook as well as an action will check that for you and PR need to respect that format to be merged.

### Documentation

Additionnaly to edit the documentation you can add/modify markdown files in the docs folder.
You can preview the doc by running 

```bash
make docs-serve
```

Then to deploy the doc you can run

```bash
make doc-deploy
```


## Deploy a new version (admins)


### Regular release

Simply create and push the tag X.Y.Z on master. 

This will create a draft release. Once you publish it (action to do by hand),
the corresponding CI will release the corresponding package version on pypi, bump the version and publish the doc.

### Beta release

Doing a beta release is a bit different, we do not use tag automation for the time being.

Simply publish a pre-release on github with the correct tag (eg, 1.1.3b1) and this will trigger the publication on pypi
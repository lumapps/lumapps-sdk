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

Then to deploy the doc you cna run

```bash
make doc-deploy
```


## Deploy a new version (admins)


### Regular release

Bump, create tag for the version and deploy the doc by running

```
make release v=<x.x.x>
```

After that the CI will make a release and release note based on commits and deploy the version to pypi.

### Beta release

Doing a beta release is a bit different, we do not do release and tag for the time being.

```
make pypi-release-beta v=<x.x.x>
```
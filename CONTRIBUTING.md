# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## Environment setup

First install dependencies and setup pre-commits hooks

```bash
make setup
```

You can run `make help` to see all available actions !

## Dev

### Code

First open an issue to discuss the matter before coding.
When your idea has been approved, create a new branch `git checkout -b <new_branch_name>` and open a Pull Request.

Before commiting you can run tests and type checks via the commands

```bash
make check
make test
```

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


## Deploy to pypi


**Only for admins** 
To deploy to pypi, bump the version and tags the version simply do

```bash 
make release
```
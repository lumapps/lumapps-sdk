# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## Environment setup

First install dependencies and setup pre-commits hooks

```bash
make setup
```

You can run `make help` to see all available actions !

## Development

**Before committing**

1. run make format to auto-format the code
2. run make check to check everything (fix any warning)
3. run make test to run the tests (fix any issue)

If you are unsure about how to fix or ignore a warning, just let the continuous integration fail, and we will help you during review.

Don't bother updating the changelog, we will take care of this.

## Deploy to pypi

To deploy to pypi, bump the version and tags the version simply do 

```bash 
make release
```
# Contributing to Lumapps SDK

We'd love for you to contribute to our source code and to make Our SDK even better than it is today! Here are the guidelines we'd like you to follow:

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Got a question or a problem?](#got-a-question-or-a-problem-)
- [Found an issue?](#found-an-issue-)
- [Want a feature?](#want-a-feature-)
- [Submission guidelines](#submission-guidelines)
- [Coding rules](#coding-rules)
- [Git commit guidelines](#git-commit-guidelines)

## <a name="got-a-question-or-a-problem-"></a> Got a question or a problem?

If you have questions about how to use Google Cloud Platform, please direct these to [StackOverflow](http://stackoverflow.com/questions/tagged/google-cloud-platform).

## <a name="found-an-issue-"></a> Found an issue?

If you find a bug in the source code or a mistake in the documentation, you can help us by submitting an issue to our [GitHub Repository](https://github.com/lumapps/lumapps-sdk/issues). Even better you can submit a Pull Request with a fix.

Please see the Submission Guidelines below.

## <a name="want-a-feature-"></a> Want a feature?

You can request a new feature by submitting an issue to our GitHub Repository. If you would like to implement a new feature then consider what kind of change it is, discuss it with us before hand in your issue, so that we can better coordinate our efforts, prevent duplication of work, and help you to craft the change so that it is successfully accepted into the project.

## <a name="submission-guidelines"></a> Submission guidelines

### Submitting an issue

Before you submit your issue search the archive, maybe your question was already answered.

If your issue appears to be a bug, and hasn't been reported, open a new issue. Help us to maximize the effort by not reporting duplicate issues. Providing the following information will increase the chances of your issue being dealt with quickly:

- **Motivation for or Use Case** - explain why this is a bug for you
- **SDK Version(s) and Python Version(s)** - is it a regression?
- **Reproduce the Error** - provide unambiguous set of steps to reproduce the error.

### Submitting a pull request
Before you submit your pull request consider the following guidelines:

* Search [GitHub](https://github.com/lumapps/lumapps-sdk/pulls) for an open or closed Pull Request
that relates to your submission. You don't want to duplicate effort.
* Make your changes in a new git branch

```shell
git checkout -b my-fix-branch master
```

* Create your patch.
* Follow our [Coding Rules](#rules).
* Commit your changes using a descriptive commit message that follows our
[commit message conventions](#commit-message-format).


* Push your branch to GitHub:

```shell
git push origin my-fix-branch
```

* In GitHub, send a pull request to `lumapps-sdk:master`.
* If we suggest changes then
* Make the required updates.
* Rebase your branch and force push to your GitHub repository (this will update your Pull Request):

```shell
git rebase master -i
git push -f
```

That's it! Thank you for your contribution!

#### After your pull request is merged

After your pull request is merged, you can safely delete your branch and pull the changes from the main (upstream) repository:

* Delete the remote branch on GitHub either through the GitHub web UI or your local shell as follows:

```shell
git push origin --delete my-fix-branch
```

* Check out the master branch:

```shell
git checkout master -f
```

* Delete the local branch:

```shell
git branch -D my-fix-branch
```

* Update your master with the latest upstream version:

```shell
git pull --ff upstream master
```

## <a name="coding-rules"></a> Coding rules


* The code must follow [The Zen of Python](https://www.python.org/dev/peps/pep-0020/) guidelines for python coding

### Docstrings

We follow the PEP484 annotations for docstring style : http://sphinxcontrib-napoleon.readthedocs.org/en/latest/example_google.html


### Strings

Always use `'{}'.format()` to format your strings (including strings concatenation) except in `logging` where you must use the native `%s` formatting : `logging.debug('Hello %s', name)`

Don't forget to prefix the format string with `u` (e.g. `u'Hello {}'.format(user)`)

Avoid:

```py
email = 'admin' + '@lumapps.com'
email = '%s@%s' % ('admin', 'lumapps', )
```

Use:

```py
email = u'{}@{}'.format('admin', 'lumapps')
email = u'{user}@{domain}'.format(user='admin', domain='lumapps.com')
```

### Forbidden functions

The functions `map` or `filter` should not be used. Prefer list comprehensions for the same behavior.

Avoid :

```py
map(int, filter(bool, [0, 1, 2, 3]))
```

Use:

```py
[int(val) for val in [0, 1, 2, 3] if val]
```

### Naming

Variables, functions, attributes, arguments, methods and modules should always be in snake_case. It means that the words must be separated by an underscore (_) and that they should not contain any uppercase letter. An exception is allowed, when function name contains an acronym (`fix_default_FS_view` having `FS` for `FileServer`)

Constants (variables defined outside of any function scope) should always be in uppercase.

Class should always be in CamelCase (with a leading uppercaser).

Prefer explicit names over short names.
Prefer short names over complex names.

### Exceptions

Use the `as` keyword instead of the comma in your except statements.

Do :

```py
try:
    doc_id = uuid.UUID(doc_id)
except (ValueError, TypeError) as e:
    pass
```

Avoid :

```py
try:
    doc_id = uuid.UUID(doc_id)
except (ValueError, TypeError), e:
    pass
```

The `as` is more explicit and python3 compatible.

### General formatting

Use [black](https://github.com/ambv/black) to format your code.

Refer to the [official documentation](https://github.com/ambv/black#editor-integration) if you need information about how to integrate it to your editor.



## <a name="git-commit-guidelines"></a> Git commit guidelines

We have very precise rules over how our git commit messages can be formatted.  This leads to **more readable messages** that are easy to follow when looking through the **project history**.

### Commit message format

Each commit message consists of a **header**, a **body** and a **footer**.  The header has a special format that includes a **type**, a **scope** and a **subject**:

```
<type> <scope>: <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

Any line of the commit message cannot be longer 100 characters! This allows the message to be easier to read on github as well as in various git tools.

### Type

Must be one of the following:

* **feat**: A new feature
* **fix**: A bug fix
* **docs**: Documentation only changes
* **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
* **refactor**: A code change that neither fixes a bug or adds a feature
* **perf**: A code change that improves performance
* **chore**: Changes to the build process or auxiliary tools and libraries such as distribution generation

### Scope

The scope could be anything specifying place of the commit change. For example `notification', 'dropdown', etc.

### Body

The body should include the motivation for the change and contrast this with previous behavior.

### Footer

The footer should contain any information about **Breaking Changes** and is also the place to reference GitHub issues that this commit **Closes**.
The breaking changes must be at the end of the commit with only on "BROKEN:" before the list of breaking changes. They must be each on a new line.

### Commit example

```
feat TOTO: TOTO for all

Before we had to do XXX. There was this and this problem. Now, by using TOTO, it's simpler and the problems are managed.

Closes PR #25
Fix #15
BROKEN:
first thing broken
second thing broken
```


## References

* [Python official glossary](https://docs.python.org/3.5/glossary.html#term-eafp)
* [Python engineering at Microsoft](https://blogs.msdn.microsoft.com/pythonengineering/2016/06/29/idiomatic-python-eafp-versus-lbyl/)

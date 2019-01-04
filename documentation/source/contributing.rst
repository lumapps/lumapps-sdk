
==============
Reporting bugs
==============

This section explains how to submit bug reports for Lumapps SDK. Following
these guidelines helps maintainers and the comunity understand your report,
reproduce the behavior, and find related reports.

Before submitting a bug
-----------------------

- Check the FAQs
- Check that your issue does not already exist in the `issue tracker <https://github.com/lumapps/lumapps-sdk/issues>`_.

How do I submit a bug
---------------------

Bugs are tracked on the `official issue tracker <ttps://github.com/lumapps/lumapps-sdk/issues>`_ where you can create a new one.

Explain the problem and include additional information to help maintainers
reproduce the problem:

- **Use a clear and descriptive title** that identifies the problem.
- **Provide the exact steps to reproduce the problem** in the clearest and most
  concise manner possible.
- **Provide specific examples to demonstrate the steps to produce the issue**. Include links to files.
- **Describe the bahavior you observe after following the steps** and point out
  what exactly is the problem with that behavior.
- **Explain which behavior you expected to see and why**

Provide more context by answering theses questions:

- **Did the problem start happening recently** (e.g after updating to a newer version) or was this always a problem ?
- If problem started happening recently, **can you reproduce the problem in an older version of the Lumapps SDK ?** What's the most recent version in which the problem doesn't happen ?
- **Can you reliably reproduce the issue ?** If not, provide details about how often the problem happens and under which conditions it normally happens.

Include details about you configuration and environment:

- **Which version of the Lumapps SDK are you using ?**.
- **Which version of python are you using ?**
- **What's the name and version og the OS you're using ?**


=======================
Suggesting enhancements
=======================

This section guides you through submitting an enhancement suggestion for the Lumapps SDK, including completly new features and minor improvments to existing functionnality.
Fllowing this guidelines helps maintainers and the community understand your suggestion and find related suggestions.

Before submitting an enhancement suggestion
-------------------------------------------

- Check that your issue does not already exist in the `issue tracker <https://github.com/lumapps/lumapps-sdk/issues>`_.

How do I submit an Enhancement suggestion ?
-------------------------------------------

- **Use a clear and decriptive title** for your suggestion.
- **Provide examples** to more clearly get what you would want.
- **Provide code snippets** if you can or **schemas** to illustrate your suggestion.

====================
Contributing to code
====================

Local development
-----------------

To contribute to the lumapps-sdk you need to clone the repo:

.. code-block:: bash

    $ git clone git@github.com:lumapps/lumapps-sdk.git
    $ cd lumapps-sdk    

Now you will need to install the required dependencies and be sure the tests are passing on your machine, we recommend you to use a virtualenv:

.. code-block:: bash

    $ virtualenv env
    $ pip install -e . && pip install -r requirements_dev.txt
    $ pytest 

We also use the `black  <https://github.com/ambv/black>`_ coding style and you must ensure that your code follows it. If not, the CI will fail and your Pull Request will not be merged.
import sys


def in_notebook():
    """
    Check if module in running in IPython kernel.

        Returns:
             ``True`` if the module is running in IPython kernel,
             ``False`` if in IPython shell or other Python shell.

        Raises:
            AnyError: If anything bad happens.

    """
    return "ipykernel" in sys.modules

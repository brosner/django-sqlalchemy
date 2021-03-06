from django.conf import settings
from django_sqlalchemy import utils
from django_sqlalchemy.test.compat import *    

def future(fn):
    """Mark a test as expected to unconditionally fail.

    Takes no arguments, omit parens when using as a decorator.
    """
    fn_name = fn.__name__
    def decorated(*args, **kw):
        try:
            fn(*args, **kw)
        except Exception, ex:
            print ("Future test '%s' failed as expected: %s " % (
                fn_name, str(ex)))
            return True
        else:
            raise AssertionError(
                "Unexpected success for future test '%s'" % fn_name)
    return _function_named(decorated, fn_name)

def fails_on(*dbs):
    """Mark a test as expected to fail on one or more database implementations.

    Unlike ``unsupported``, tests marked as ``fails_on`` will be run
    for the named databases.  The test is expected to fail and the unit test
    logic is inverted: if the test fails, a success is reported.  If the test
    succeeds, a failure is reported.
    """
    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if utils.db_label not in dbs:
                return fn(*args, **kw)
            else:
                try:
                    fn(*args, **kw)
                except Exception, ex:
                    print ("'%s' failed as expected on DB implementation "
                           "'%s': %s" % (
                        fn_name, utils.db_label, str(ex)))
                    return True
                else:
                    raise AssertionError(
                        "Unexpected success for '%s' on DB implementation '%s'" %
                        (fn_name, utils.db_label))
        return _function_named(maybe, fn_name)
    return decorate

def fails_on_everything_except(*dbs):
    """Mark a test as expected to fail on most database implementations.

    Like ``fails_on``, except failure is the expected outcome on all
    databases except those listed.
    """

    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if utils.db_label in dbs:
                return fn(*args, **kw)
            else:
                try:
                    fn(*args, **kw)
                except Exception, ex:
                    print ("'%s' failed as expected on DB implementation "
                           "'%s': %s" % (
                        fn_name, utils.db_label, str(ex)))
                    return True
                else:
                    raise AssertionError(
                        "Unexpected success for '%s' on DB implementation '%s'" %
                        (fn_name, utils.db_label))
        return _function_named(maybe, fn_name)
    return decorate

def unsupported(*dbs):
    """Mark a test as unsupported by one or more database implementations.

    'unsupported' tests will be skipped unconditionally.  Useful for feature
    tests that cause deadlocks or other fatal problems.
    """

    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if utils.db_label in dbs:
                print "'%s' unsupported on DB implementation '%s'" % (
                    fn_name, utils.db_label)
                return True
            else:
                return fn(*args, **kw)
        return _function_named(maybe, fn_name)
    return decorate

def requires(app_label):
    """Mark a test as expected to fail for the app specified if the app
    is not included in INSTALLED_APPS.
    """
    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            for app_name in settings.INSTALLED_APPS:
                if app_label == app_name.split('.')[-1]:
                    return fn(*args, **kw)
            return True
        return _function_named(maybe, fn_name)
    return decorate

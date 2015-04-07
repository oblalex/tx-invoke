# -*- coding: utf-8 -*-

from functools import wraps


def task_on_callbacks(*task_args, **task_kwargs):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            from twisted.internet import defer, reactor

            def errback(failure):
                print(failure)

            deferred = defer.inlineCallbacks(function)(*args, **kwargs)
            deferred.addErrback(errback)
            deferred.addBoth(lambda unused: reactor.stop())

            reactor.run()

        from invoke.tasks import Task, task as task_decoracor

        class TaskProxy(Task):

            def __init__(self, task):
                self.task = task
                self.__name__ = self.task.__name__
                self.__module__ = self.task.__module__
                self.__doc__ = self.task.__doc__

            def __call__(self, *args, **kwargs):
                original_function, self.task.body = self.task.body, wrapper
                result = self.task(*args, **kwargs)
                self.task.body = original_function
                return result

            def __getattr__(self, key):
                return getattr(self.task, key)

        task = task_decoracor(*task_args, **task_kwargs)(function)
        return TaskProxy(task)

    return decorator

# Copyright (c) 2015 Uber Technologies, Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import

import sys
from concurrent.futures import Future


class SettableFuture(Future):
    """Future with support for `set_result` and `set_exception`."""
    # These operations are implemented in Future but are not part of the
    # "public interface". This class makes the dependency on those methods
    # more concrete. If the methods ever get removed, we can implement our own
    # versions.

    def set_result(self, result):
        """Set the result of this Future to the given value.

        All consumers waiting on the output of this future will unblock.

        :param result:
            Result value of the future
        """
        return super(SettableFuture, self).set_result(result)

    def set_exception(self, exception=None, traceback=None):
        """Put an exception into this Future.

        All blocked `result()` calls will re-raise the given exception. If the
        exception or the traceback is omitted, they will automatically be
        determined using `sys.exc_info`.

        :param exception:
            Exception for the Future
        :param traceback:
            Traceback of the exception
        """
        if not exception or not traceback:
            exception, traceback = sys.exc_info()[1:]
        super(SettableFuture, self).set_exception_info(exception, traceback)


def transform_future(future, function):
    """Transform the output of the given Future using the given function."""
    assert function is not None
    assert isinstance(future, Future)

    result_future = SettableFuture()

    def on_done(f):
        try:
            output = f.result()
            result = function(output)
        except:
            result_future.set_exception()
        else:
            result_future.set_result(result)

    future.add_done_callback(on_done)
    return result_future
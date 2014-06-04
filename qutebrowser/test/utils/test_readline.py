# Copyright 2014 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=missing-docstring

"""Tests for qutebrowser.utils.readline."""

import inspect
import unittest
from unittest import TestCase
from unittest.mock import Mock

from PyQt5.QtWidgets import QLineEdit

import qutebrowser.utils.readline as readline


class FakeQApplication:

    """Stub to insert as QApplication module."""

    def __init__(self, focus):
        # pylint: disable=invalid-name
        self.focusWidget = Mock(return_value=focus)
        self.instance = Mock(return_value=self)


class NoneWidgetTests(TestCase):

    """Tests when the focused widget is None."""

    def setUp(self):
        readline.QApplication = FakeQApplication(None)
        self.bridge = readline.ReadlineBridge()

    def test_none(self):
        """Test if there are no exceptions when the widget is None."""
        for name, method in inspect.getmembers(self.bridge, inspect.ismethod):
            if name.startswith('rl_'):
                method()


class ReadlineBridgeTest(TestCase):

    """Tests for readline bridge."""

    def setUp(self):
        self.qle = Mock()
        self.qle.__class__ = QLineEdit
        readline.QApplication = FakeQApplication(self.qle)
        self.bridge = readline.ReadlineBridge()

    def _set_selected_text(self, text):
        """Set the value the fake QLineEdit should return for selectedText."""
        self.qle.configure_mock(**{'selectedText.return_value': text})

    def test_rl_backward_char(self):
        self.bridge.rl_backward_char()
        self.qle.cursorBackward.assert_called_with(False)

    def test_rl_forward_char(self):
        self.bridge.rl_forward_char()
        self.qle.cursorForward.assert_called_with(False)

    def test_rl_backward_word(self):
        self.bridge.rl_backward_word()
        self.qle.cursorWordBackward.assert_called_with(False)

    def test_rl_forward_word(self):
        self.bridge.rl_forward_word()
        self.qle.cursorWordForward.assert_called_with(False)

    def test_rl_beginning_of_line(self):
        self.bridge.rl_beginning_of_line()
        self.qle.home.assert_called_with(False)

    def test_rl_end_of_line(self):
        self.bridge.rl_end_of_line()
        self.qle.end.assert_called_with(False)

    def test_rl_unix_line_discard(self):
        """Set a selected text, delete it, see if it comes back with yank."""
        self._set_selected_text("delete test")
        self.bridge.rl_unix_line_discard()
        self.qle.home.assert_called_with(True)
        self.assertEqual(self.bridge.deleted[self.qle], "delete test")
        self.qle.del_.assert_called_with()
        self.bridge.rl_yank()
        self.qle.insert.assert_called_with("delete test")

    def test_rl_kill_line(self):
        """Set a selected text, delete it, see if it comes back with yank."""
        self._set_selected_text("delete test")
        self.bridge.rl_kill_line()
        self.qle.end.assert_called_with(True)
        self.assertEqual(self.bridge.deleted[self.qle], "delete test")
        self.qle.del_.assert_called_with()
        self.bridge.rl_yank()
        self.qle.insert.assert_called_with("delete test")

    def test_rl_unix_word_rubout(self):
        """Set a selected text, delete it, see if it comes back with yank."""
        self._set_selected_text("delete test")
        self.bridge.rl_unix_word_rubout()
        self.qle.cursorWordBackward.assert_called_with(True)
        self.assertEqual(self.bridge.deleted[self.qle], "delete test")
        self.qle.del_.assert_called_with()
        self.bridge.rl_yank()
        self.qle.insert.assert_called_with("delete test")

    def test_rl_kill_word(self):
        """Set a selected text, delete it, see if it comes back with yank."""
        self._set_selected_text("delete test")
        self.bridge.rl_kill_word()
        self.qle.cursorWordForward.assert_called_with(True)
        self.assertEqual(self.bridge.deleted[self.qle], "delete test")
        self.qle.del_.assert_called_with()
        self.bridge.rl_yank()
        self.qle.insert.assert_called_with("delete test")

    def test_rl_yank_no_text(self):
        """Test yank without having deleted anything."""
        self.bridge.rl_yank()
        self.assertFalse(self.qle.insert.called)


if __name__ == '__main__':
    unittest.main()
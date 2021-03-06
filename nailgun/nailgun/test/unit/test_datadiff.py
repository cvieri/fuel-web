# -*- coding: utf-8 -*-

#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import six

from nailgun.utils import datadiff

from nailgun.test import base


class TestDataDiff(base.BaseUnitTest):
    def check_diff(self, data1, data2, added, deleted):
        diff1 = datadiff.diff(data1, data2)
        self.assertEqual(added, diff1.added)
        self.assertEqual(deleted, diff1.deleted)
        diff2 = datadiff.diff(data2, data1)
        self.assertEqual(deleted, diff2.added)
        self.assertEqual(added, diff2.deleted)
        diff3 = datadiff.diff(data2, data2)
        self.assertFalse(diff3.added)
        self.assertFalse(diff3.deleted)

    def test_diff_dict(self):
        self.check_diff(
            {'a': 1, 'b': 2, 'c': {'d': {'e': 3}}},
            {'a': 1, 'b': 2, 'd': {'e': 3}},
            {'d': {'e': 3}},
            {'c': {'d': {'e': 3}}}
        )

    def test_diff_list(self):
        self.check_diff([1, 2, 3], [2, 3, 4], [4], [1])
        self.check_diff(
            [{'a': 1, 'b': '1'}, {'a': 3, 'b': '3'}],
            [{'a': 1, 'b': '2'}, {'a': 2, 'b': '3'}, {'a': 3, 'b': '4'}],
            [{'a': 1, 'b': '2'}, {'a': 2, 'b': '3'}, {'a': 3, 'b': '4'}],
            [{'a': 1, 'b': '1'}, {'a': 3, 'b': '3'}]
        )

    def test_diff_set(self):
        self.check_diff({1, 2, 3}, {2, 3, 4}, {4}, {1})

    def test_diff_range(self):
        diff1 = datadiff.diff(six.moves.range(3), six.moves.range(1, 4))
        self.assertEqual([3], diff1.added)
        self.assertEqual([0], diff1.deleted)

    def test_diff_iterable(self):
        data1 = ({x: x} for x in six.moves.range(3))
        data2 = ({x: x} for x in six.moves.range(1, 4))
        diff1 = datadiff.diff(data1, data2)
        self.assertEqual([{3: 3}], diff1.added)
        self.assertEqual([{0: 0}], diff1.deleted)
        data1 = six.moves.filter(None, six.moves.range(3))
        data2 = six.moves.filter(None, six.moves.range(4))
        diff2 = datadiff.diff(data1, data2)
        self.assertEqual([3], diff2.added)
        self.assertEqual([], diff2.deleted)

    def test_diff_simple(self):
        diff = datadiff.diff('abc\nbcd', 'bcd\ncda')
        self.assertEqual(['cda'], diff.added)
        self.assertEqual(['abc'], diff.deleted)

    def test_diff_for_different_types(self):
        d = datadiff.diff({1, 2}, [1, 2])
        self.assertEqual([1, 2], d.added)
        self.assertEqual({1, 2}, d.deleted)

    def test_diff_for_tuple_of_lists(self):
        self.check_diff(([1], [2], [3]), ([2], [3], [4]), [[4]], [[1]])

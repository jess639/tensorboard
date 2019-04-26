# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abc
import collections
import os
import time

from google.protobuf import text_format
import six
import tensorflow as tf

<<<<<<< HEAD
=======
try:
  # python version >= 3.3
  from unittest import mock  # pylint: disable=g-import-not-at-top
except ImportError:
  import mock  # pylint: disable=g-import-not-at-top,unused-import

>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~
from tensorboard import test
from tensorboard.plugins.hparams import api as hp
from tensorboard.plugins.hparams import api_pb2
from tensorboard.plugins.hparams import metadata
from tensorboard.plugins.hparams import plugin_data_pb2
<<<<<<< HEAD
from tensorboard.util import test_util
=======


tf.compat.v1.enable_eager_execution()
>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~


class ExperimentTest(test.TestCase):
  def test_summary_pb(self):
    hparams = [
        hp.HParam("learning_rate", hp.RealInterval(1e-2, 1e-1)),
        hp.HParam("dense_layers", hp.IntInterval(2, 7)),
        hp.HParam("optimizer", hp.Discrete(["adam", "sgd"])),
        hp.HParam("who_knows_what"),
        hp.HParam(
            "magic",
            hp.Discrete([False, True]),
            display_name="~*~ Magic ~*~",
            description="descriptive",
        ),
    ]
    metrics = [
        hp.Metric("samples_per_second"),
        hp.Metric(group="train", tag="batch_loss", display_name="loss (train)"),
        hp.Metric(
            group="validation",
            tag="epoch_accuracy",
            display_name="accuracy (val.)",
            description="Accuracy on the _validation_ dataset.",
            dataset_type=hp.Metric.VALIDATION,
        ),
    ]
    experiment = hp.Experiment(
        hparams=hparams,
        metrics=metrics,
        user="zalgo",
        description="nothing to see here; move along",
        time_created_secs=1555624767,
    )

    self.assertEqual(experiment.hparams, hparams)
    self.assertEqual(experiment.metrics, metrics)
    self.assertEqual(experiment.user, "zalgo"),
    self.assertEqual(experiment.description, "nothing to see here; move along")
    self.assertEqual(experiment.time_created_secs, 1555624767)

    expected_experiment_pb = api_pb2.Experiment()
    text_format.Merge(
        """
        description: "nothing to see here; move along"
        user: "zalgo"
        time_created_secs: 1555624767.0
        hparam_infos {
          name: "learning_rate"
          type: DATA_TYPE_FLOAT64
          domain_interval {
            min_value: 0.01
            max_value: 0.1
          }
        }
        hparam_infos {
          name: "dense_layers"
          type: DATA_TYPE_FLOAT64
          domain_interval {
            min_value: 2
            max_value: 7
          }
        }
        hparam_infos {
          name: "optimizer"
          type: DATA_TYPE_STRING
          domain_discrete {
            values {
              string_value: "adam"
            }
            values {
              string_value: "sgd"
            }
          }
        }
        hparam_infos {
          name: "who_knows_what"
        }
        hparam_infos {
          name: "magic"
          type: DATA_TYPE_BOOL
          display_name: "~*~ Magic ~*~"
          description: "descriptive"
          domain_discrete {
            values {
              bool_value: false
            }
            values {
              bool_value: true
            }
          }
        }
        metric_infos {
          name {
            tag: "samples_per_second"
          }
        }
        metric_infos {
          name {
            group: "train"
            tag: "batch_loss"
          }
          display_name: "loss (train)"
        }
        metric_infos {
          name {
            group: "validation"
            tag: "epoch_accuracy"
          }
          display_name: "accuracy (val.)"
          description: "Accuracy on the _validation_ dataset."
          dataset_type: DATASET_VALIDATION
        }
        """,
        expected_experiment_pb,
    )
    actual_summary_pb = experiment.summary_pb()
    plugin_content = actual_summary_pb.value[0].metadata.plugin_data.content
    self.assertEqual(
        metadata.parse_experiment_plugin_data(plugin_content),
        expected_experiment_pb,
    )

<<<<<<< HEAD
  def _assert_unique_summary(self, logdir, summary_pb):
    """Test that `logdir` contains exactly one summary, `summary_pb`.

    Specifically, `logdir` must be a directory containing exactly one
    entry, which must be an events file of whose events exactly one is a
    summary, which must be equal to `summary_pb`.

    Args:
      logdir: String path to a logdir.
      summary_pb: A `summary_pb2.Summary` object.
    """
    files = os.listdir(logdir)
    self.assertEqual(len(files), 1, files)
    events_file = os.path.join(logdir, files[0])
    for event in tf.compat.v1.train.summary_iterator(events_file):
      if event.WhichOneof("what") != "summary":
        continue
      self.assertEqual(event.summary, summary_pb)
      break
    else:
      self.fail("No summary data found")

  @test_util.run_v2_only("Requires eager summary writing semantics.")
  def test_write_experiment_v2(self):
    experiment = hp.Experiment(
        hparams=[hp.HParam("num_units", hp.Discrete([16, 32]))],
        metrics=[hp.Metric("accuracy")],
    )
    logdir = os.path.join(self.get_temp_dir(), "logs")
    with tf.compat.v2.summary.create_file_writer(logdir).as_default() as w:
      self.assertTrue(hp.experiment(experiment))
      w.close()
    self._assert_unique_summary(logdir, experiment.summary_pb())

  @test_util.run_v2_only("Requires eager summary writing semantics.")
  def test_write_experiment_v2_no_default_writer(self):
    experiment = hp.Experiment(
        hparams=[hp.HParam("num_units", hp.Discrete([16, 32]))],
        metrics=[hp.Metric("accuracy")],
    )
    self.assertFalse(hp.experiment(experiment))  # no writer

  @test_util.run_v1_only("Requires graph-mode summary writing semantics.")
  def test_write_experiment_v1(self):
    experiment = hp.Experiment(
        hparams=[hp.HParam("num_units", hp.Discrete([16, 32]))],
        metrics=[hp.Metric("accuracy")],
    )
    logdir = os.path.join(self.get_temp_dir(), "logs")
    with tf.compat.v1.Session() as sess:
      with tf.compat.v2.summary.create_file_writer(logdir).as_default() as w:
        with tf.compat.v2.summary.record_if(True):
          tf.contrib.summary.initialize()
          self.assertTrue(sess.run(hp.experiment(experiment)))
          w.close()
    self._assert_unique_summary(logdir, experiment.summary_pb())

=======
>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~

class IntIntervalTest(test.TestCase):
  def test_simple(self):
    domain = hp.IntInterval(3, 7)
    self.assertEqual(domain.min_value, 3)
    self.assertEqual(domain.max_value, 7)
    self.assertEqual(domain.dtype, int)

  def test_singleton_domain(self):
    domain = hp.IntInterval(61, 61)
    self.assertEqual(domain.min_value, 61)
    self.assertEqual(domain.max_value, 61)
    self.assertEqual(domain.dtype, int)

  def test_non_ints(self):
    with six.assertRaisesRegex(
        self, TypeError, "min_value must be an int: -inf"):
      hp.IntInterval(float("-inf"), 0)
    with six.assertRaisesRegex(
        self, TypeError, "max_value must be an int: 'eleven'"):
      hp.IntInterval(7, "eleven")

  def test_backward_endpoints(self):
    with six.assertRaisesRegex(
        self, ValueError, "123 > 45"):
      hp.IntInterval(123, 45)


class RealIntervalTest(test.TestCase):
  def test_simple(self):
    domain = hp.RealInterval(3.1, 7.7)
    self.assertEqual(domain.min_value, 3.1)
    self.assertEqual(domain.max_value, 7.7)
    self.assertEqual(domain.dtype, float)

  def test_singleton_domain(self):
    domain = hp.RealInterval(61.318, 61.318)
    self.assertEqual(domain.min_value, 61.318)
    self.assertEqual(domain.max_value, 61.318)
    self.assertEqual(domain.dtype, float)

  def test_infinite_domain(self):
    inf = float("inf")
    domain = hp.RealInterval(-inf, inf)
    self.assertEqual(domain.min_value, -inf)
    self.assertEqual(domain.max_value, inf)
    self.assertEqual(domain.dtype, float)

  def test_non_ints(self):
    with six.assertRaisesRegex(
        self, TypeError, "min_value must be a float: True"):
      hp.RealInterval(True, 2.0)
    with six.assertRaisesRegex(
        self, TypeError, "max_value must be a float: 'wat'"):
      hp.RealInterval(1.2, "wat")

  def test_backward_endpoints(self):
    with six.assertRaisesRegex(
        self, ValueError, "2.1 > 1.2"):
      hp.RealInterval(2.1, 1.2)


class DiscreteTest(test.TestCase):
  def test_simple(self):
    domain = hp.Discrete([1, 2, 5])
    self.assertEqual(domain.values, [1, 2, 5])
    self.assertEqual(domain.dtype, int)

  def test_values_sorted(self):
    domain = hp.Discrete([2, 3, 1])
    self.assertEqual(domain.values, [1, 2, 3])
    self.assertEqual(domain.dtype, int)

  def test_empty_with_explicit_dtype(self):
    domain = hp.Discrete([], dtype=bool)
    self.assertIs(domain.dtype, bool)
    self.assertEqual(domain.values, [])

  def test_empty_with_unspecified_dtype(self):
    with six.assertRaisesRegex(
        self, ValueError, "Empty domain with no dtype specified"):
      hp.Discrete([])

  def test_dtype_mismatch(self):
    with six.assertRaisesRegex(
<<<<<<< HEAD
        self, ValueError, r"dtype mismatch: not isinstance\(2, str\)"):
=======
        self, TypeError, r"dtype mismatch: not isinstance\(2, str\)"):
>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~
      hp.Discrete(["one", 2])


class KerasCallbackTest(test.TestCase):
<<<<<<< HEAD
  def setUp(self):
    super(KerasCallbackTest, self).setUp()
=======

  def setUp(self):
    super(KerasCallbackTest, self).setUp()
    self.logdir = os.path.join(self.get_temp_dir(), "logs")

  def _initialize_model(self, writer):
>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~
    HP_DENSE_NEURONS = hp.HParam("dense_neurons", hp.IntInterval(4, 16))
    self.hparams = {
        "optimizer": "adam",
        HP_DENSE_NEURONS: 8,
    }
    self.model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(self.hparams[HP_DENSE_NEURONS], input_shape=(1,)),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])
    self.model.compile(loss="mse", optimizer=self.hparams["optimizer"])
<<<<<<< HEAD
    self.logdir = os.path.join(self.get_temp_dir(), "logs")
    self.callback = hp.KerasCallback(
        self.logdir,
        self.hparams,
        group_name="psl27",
    )

  @test_util.run_v2_only("Requires eager mode.")
  def test_eager(self):
    self.model.fit(x=[(1,)], y=[(2,)], callbacks=[self.callback])
=======
    self.callback = hp.KerasCallback(writer, self.hparams, group_name="psl27")

  def test_eager(self):
    def mock_time():
      mock_time.time += 1
      return mock_time.time
    mock_time.time = 1556227801.875
    initial_time = mock_time.time
    with mock.patch("time.time", mock_time):
      self._initialize_model(writer=self.logdir)
      self.model.fit(x=[(1,)], y=[(2,)], callbacks=[self.callback])
    final_time = mock_time.time
>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~

    files = os.listdir(self.logdir)
    self.assertEqual(len(files), 1, files)
    events_file = os.path.join(self.logdir, files[0])
    plugin_data = []
    for event in tf.compat.v1.train.summary_iterator(events_file):
      if event.WhichOneof("what") != "summary":
        continue
      self.assertEqual(len(event.summary.value), 1, event.summary.value)
      value = event.summary.value[0]
      self.assertEqual(
          value.metadata.plugin_data.plugin_name,
          metadata.PLUGIN_NAME,
      )
      plugin_data.append(value.metadata.plugin_data.content)

    self.assertEqual(len(plugin_data), 2, plugin_data)
    (start_plugin_data, end_plugin_data) = plugin_data
    start_pb = metadata.parse_session_start_info_plugin_data(start_plugin_data)
    end_pb = metadata.parse_session_end_info_plugin_data(end_plugin_data)

<<<<<<< HEAD
    # Remove any dependence on system time.
    start_pb.start_time_secs = 123.45
    end_pb.end_time_secs = 234.56
=======
    # We're not the only callers of `time.time`; Keras calls it
    # internally an unspecified number of times, so we're not guaranteed
    # to know the exact values. Instead, we perform relative checks...
    self.assertGreater(start_pb.start_time_secs, initial_time)
    self.assertLess(start_pb.start_time_secs, end_pb.end_time_secs)
    self.assertLessEqual(start_pb.start_time_secs, final_time)
    # ...and then stub out the times for proto equality checks below.
    start_pb.start_time_secs = 1234.5
    end_pb.end_time_secs = 6789.0
>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~

    expected_start_pb = plugin_data_pb2.SessionStartInfo()
    text_format.Merge(
        """
<<<<<<< HEAD
        start_time_secs: 123.45
=======
        start_time_secs: 1234.5
>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~
        group_name: "psl27"
        hparams {
          key: "optimizer"
          value {
            string_value: "adam"
          }
        }
        hparams {
          key: "dense_neurons"
          value {
            number_value: 8.0
          }
        }
        """,
        expected_start_pb,
    )
    self.assertEqual(start_pb, expected_start_pb)

    expected_end_pb = plugin_data_pb2.SessionEndInfo()
    text_format.Merge(
        """
<<<<<<< HEAD
        end_time_secs: 234.56
=======
        end_time_secs: 6789.0
>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~
        status: STATUS_SUCCESS
        """,
        expected_end_pb,
    )
    self.assertEqual(end_pb, expected_end_pb)

<<<<<<< HEAD

  @test_util.run_v1_only("Requires non-eager mode.")
  def test_non_eager_failure(self):
    with six.assertRaisesRegex(
        self, RuntimeError, "only supported in TensorFlow eager mode"):
      self.model.fit(x=[(1,)], y=[(2,)], callbacks=[self.callback])

=======
  def test_explicit_writer(self):
    writer = tf.compat.v2.summary.create_file_writer(
        self.logdir,
        filename_suffix=".magic",
    )
    self._initialize_model(writer=writer)
    self.model.fit(x=[(1,)], y=[(2,)], callbacks=[self.callback])

    files = os.listdir(self.logdir)
    self.assertEqual(len(files), 1, files)
    filename = files[0]
    self.assertTrue(filename.endswith(".magic"), filename)
    # We'll assume that the contents are correct, as in the case where
    # the file writer was constructed implicitly.

  def test_non_eager_failure(self):
    with tf.compat.v1.Graph().as_default():
      assert not tf.executing_eagerly()
      self._initialize_model(writer=self.logdir)
      with six.assertRaisesRegex(
          self, RuntimeError, "only supported in TensorFlow eager mode"):
        self.model.fit(x=[(1,)], y=[(2,)], callbacks=[self.callback])

  def test_reuse_failure(self):
    self._initialize_model(writer=self.logdir)
    self.model.fit(x=[(1,)], y=[(2,)], callbacks=[self.callback])
    with six.assertRaisesRegex(
        self, RuntimeError, "cannot be reused across training sessions"):
      self.model.fit(x=[(1,)], y=[(2,)], callbacks=[self.callback])

  def test_invalid_writer(self):
    with six.assertRaisesRegex(
        self, TypeError, "writer must be a `SummaryWriter` or `str`, not None"):
      hp.KerasCallback(writer=None, hparams={})

>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~
  def test_duplicate_hparam_names_across_object_and_string(self):
    hparams = {
        "foo": 1,
        hp.HParam("foo"): 1,
    }
    with six.assertRaisesRegex(
        self, ValueError, "multiple values specified for hparam 'foo'"):
<<<<<<< HEAD
      hp.KerasCallback(self.logdir, hparams)
=======
      hp.KerasCallback(self.get_temp_dir(), hparams)
>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~

  def test_duplicate_hparam_names_from_two_objects(self):
    hparams = {
        hp.HParam("foo"): 1,
        hp.HParam("foo"): 1,
    }
    with six.assertRaisesRegex(
        self, ValueError, "multiple values specified for hparam 'foo'"):
<<<<<<< HEAD
      hp.KerasCallback(self.logdir, hparams)
=======
      hp.KerasCallback(self.get_temp_dir(), hparams)
>>>>>>> 15331f807a5a7a640136a7fa546d1c8c970ea430~


if __name__ == "__main__":
  test.main()

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

image_size = 48
num_channels = 1
num_classes = 7

"""
Method for building BKVGG8 CNN architecture. 
"""
def cnn_vgg8(features, labels, mode, params):
    with tf.name_scope("input_layer"):
        input = tf.cast(tf.reshape(features, [-1, image_size, image_size, num_channels]), tf.float32)

    with tf.name_scope("rect_1"):
        with tf.name_scope("conv3_32_1"):
            rect1_conv1 = tf.layers.conv2d(
                inputs=input,
                filters=32,
                kernel_size=[3, 3],
                padding="same",
                activation=tf.nn.relu,
                bias_initializer=tf.zeros_initializer(),
                kernel_initializer=tf.contrib.layers.xavier_initializer_conv2d()
            )

        mean, variance = tf.nn.moments(rect1_conv1, [0, 1, 2])
        rect1_normalized_conv1 = tf.nn.batch_normalization(rect1_conv1, mean, variance, None, None, 0.0001)

        with tf.name_scope("max_pool"):
            rect1_max_pool = tf.layers.max_pooling2d(
                inputs=rect1_normalized_conv1,
                pool_size=[2, 2],
                strides=2,
                padding="valid"
            )

    with tf.name_scope("rect_2"):
        with tf.name_scope("conv3_64_1"):
            rect2_conv1 = tf.layers.conv2d(
                inputs=rect1_max_pool,
                filters=64,
                kernel_size=[3, 3],
                padding="same",
                activation=tf.nn.relu,
                bias_initializer=tf.zeros_initializer(),
                kernel_initializer=tf.contrib.layers.xavier_initializer_conv2d()
            )

        mean, variance = tf.nn.moments(rect2_conv1, [0, 1, 2])
        rect2_normalized_conv1 = tf.nn.batch_normalization(rect2_conv1, mean, variance, None, None, 0.0001)

        with tf.name_scope("max_pool"):
            rect2_max_pool = tf.layers.max_pooling2d(
                inputs=rect2_normalized_conv1,
                pool_size=[2, 2],
                strides=2,
                padding="valid"
            )

    with tf.name_scope("rect_3"):
        with tf.name_scope("conv3_128_1"):
            rect3_conv1 = tf.layers.conv2d(
                inputs=rect2_max_pool,
                filters=128,
                kernel_size=[3, 3],
                padding="same",
                activation=tf.nn.relu,
                bias_initializer=tf.zeros_initializer(),
                kernel_initializer=tf.contrib.layers.xavier_initializer_conv2d()
            )

        mean, variance = tf.nn.moments(rect3_conv1, [0, 1, 2])
        rect3_normalized_conv1 = tf.nn.batch_normalization(rect3_conv1, mean, variance, None, None, 0.0001)

        with tf.name_scope("max_pool"):
            rect3_max_pool = tf.layers.max_pooling2d(
                inputs=rect3_normalized_conv1,
                pool_size=[2, 2],
                strides=2,
                padding="valid"
            )

    with tf.name_scope("rect_4"):
        with tf.name_scope("conv3_256_1"):
            rect4_conv1 = tf.layers.conv2d(
                inputs=rect3_max_pool,
                filters=256,
                kernel_size=[3, 3],
                padding="same",
                activation=tf.nn.relu,
                bias_initializer=tf.zeros_initializer(),
                kernel_initializer=tf.contrib.layers.xavier_initializer_conv2d()
            )

        mean, variance = tf.nn.moments(rect4_conv1, [0, 1, 2])
        rect4_normalized_conv1 = tf.nn.batch_normalization(rect4_conv1, mean, variance, None, None, 0.0001)

        with tf.name_scope("conv3_256_2"):
            rect4_conv2 = tf.layers.conv2d(
                inputs=rect4_normalized_conv1,
                filters=256,
                kernel_size=[3, 3],
                padding="same",
                activation=tf.nn.relu,
                bias_initializer=tf.zeros_initializer(),
                kernel_initializer=tf.contrib.layers.xavier_initializer_conv2d()
            )

        mean, variance = tf.nn.moments(rect4_conv2, [0, 1, 2])
        rect4_normalized_conv2 = tf.nn.batch_normalization(rect4_conv2, mean, variance, None, None, 0.0001)

        with tf.name_scope("flatten_units"):
            flatten_units = tf.reshape(rect4_normalized_conv2, [-1, 6 * 6 * 256])

    with tf.name_scope("fccs"):
        with tf.name_scope("fcc_1"):
            fcc1 = tf.layers.dense(
                inputs=flatten_units,
                units=256,
                activation=tf.nn.relu,
                bias_initializer=tf.zeros_initializer(),
                kernel_initializer=tf.contrib.layers.xavier_initializer()
            )
            fcc1 = tf.layers.dropout(fcc1, 0.5)

        with tf.name_scope("fcc_2"):
            fcc2 = tf.layers.dense(
                inputs=fcc1,
                units=256,
                activation=tf.nn.relu,
                bias_initializer=tf.zeros_initializer(),
                kernel_initializer=tf.contrib.layers.xavier_initializer()
            )
            fcc2 = tf.layers.dropout(fcc2, 0.5)

    with tf.name_scope("logits"):
        logits = tf.layers.dense(
            inputs=fcc2,
            units=num_classes,
            activation=tf.nn.softmax
        )

    predictions = {
        "probabilities": logits,
        "rect1_conv1": rect1_conv1,
        "rect2_conv1": rect2_conv1,
        "rect3_conv1": rect3_conv1,
        "rect4_conv1": rect4_conv1,
        "rect4_conv2": rect4_conv2,
        "classes": tf.argmax(logits, axis=1)
    }

    tf.summary.histogram("rect1_conv1_activations", rect1_conv1)
    tf.summary.histogram("rect2_conv1_activations", rect2_conv1)
    tf.summary.histogram("rect3_conv1_activations", rect3_conv1)
    tf.summary.histogram("rect4_conv1_activations", rect4_conv1)
    tf.summary.histogram("rect4_conv2_activations", rect4_conv2)
    tf.contrib.layers.summarize_collection(tf.GraphKeys.TRAINABLE_VARIABLES)

    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode, predictions=predictions)

    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
    accuracy = tf.metrics.accuracy(labels=labels, predictions=tf.argmax(logits, axis=1))

    tf.summary.scalar("Loss", loss)
    tf.summary.scalar("Accuracy", accuracy[1])

    logging_hook = tf.train.LoggingTensorHook({"loss": loss, "accuracy": accuracy[1], "step": tf.train.get_global_step()}, every_n_iter=1)

    summary_hook = tf.train.SummarySaverHook(
        params["save_steps"],
        output_dir=params["logdir"],
        summary_op=tf.summary.merge_all()
    )

    if mode == tf.estimator.ModeKeys.EVAL:
        eval_metrics = {
            "accuracy": accuracy
        }
        return tf.estimator.EstimatorSpec(mode, loss=loss, eval_metric_ops=eval_metrics)

    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.AdamOptimizer(learning_rate=params["learning_rate"])
        train_op = optimizer.minimize(loss=loss, global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op, training_hooks=[summary_hook, logging_hook])
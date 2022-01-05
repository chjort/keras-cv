import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras import layers


class MixUp(layers.Layer):
    """
    MixUp implements the MixUp data augmentation technique as proposed in https://arxiv.org/abs/1710.09412.

    Args:
        num_classes: number of classes in the dataset.
        alpha: alpha parameter for the sample distribution.
        probability: probability to apply the CutMix augmentation.
        label_smoothing: coefficient used in label smoothing.

    Sample usage:
    ```python
    (x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
    mixup = MixUp(10)
    augmented_data, updated_labels = mixup(x_train, y_train)
    ```
    """
    def __init__(
        self,
        num_classes,
        alpha=0.8,
        probability=1.0,
        num_classes=None,
        label_smoothing=0.0,
        **kwargs
    ):
        super(MixUp, self).__init__(*kwargs)
        self.alpha = alpha
        self.probability = probability
        self.num_classes = num_classes
        self.label_smoothing = label_smoothing

    @staticmethod
    def _sample_from_beta(alpha, beta, shape):
        sample_alpha = tf.random.gamma(shape, 1.0, beta=alpha)
        sample_beta = tf.random.gamma(shape, 1.0, beta=beta)
        return sample_alpha / (sample_alpha + sample_beta)

    def call(self, images, labels):
        augment_cond = tf.less(
            tf.random.uniform(shape=[], minval=0.0, maxval=1.0), self.probability
        )
        # pylint: disable=g-long-lambda
        mixup_augment = lambda: self._update_labels(*self._mixup(images, labels))
        no_augment = lambda: (images, self._smooth_labels(labels))
        return tf.cond(augment_cond, mixup_augment, no_augment)

    def _mixup(self, images, labels):
        lambda_sample = MixUp._sample_from_beta(self.alpha, self.alpha, labels.shape)
        lambda_sample = tf.reshape(lam, [-1, 1, 1, 1])
        images = lambda_sample * images + (1.0 - lambda_sample) * tf.reverse(images, [0])

        return images, labels, tf.squeeze(lambda_sample)

    def _update_labels(self, images, labels, lambda_sample):
        labels_1 = self._smooth_labels(labels)
        labels_2 = tf.reverse(labels_1, [0])

        lambda_sample = tf.reshape(lambda_sample, [-1, 1])
        labels = lambda_sample * labels_1 + (1.0 - lambda_sample) * labels_2

        return images, labels

    def _smooth_labels(self, labels):
        label_smoothing = self.label_smoothing or 0.0
        off_value = label_smoothing / self.num_classes
        on_value = 1.0 - label_smoothing + off_value

        smooth_labels = tf.one_hot(
            labels, self.num_classes, on_value=on_value, off_value=off_value
        )
        return smooth_labels
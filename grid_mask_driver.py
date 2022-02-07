"""gridmask_demo.py shows how to use the GridMask preprocessing layer.

Operates on the oxford_flowers102 dataset.  In this script the flowers
are loaded, then are passed through the preprocessing layers.
Finally, they are shown using matplotlib.
"""

import matplotlib.pyplot as plt
import tensorflow as tf

from keras_cv.utils import fill_utils

IMG_SHAPE = (3, 224, 224)

img = tf.ones(IMG_SHAPE)

# %%
ratio = 0.6

batch_size, img_h, img_w = IMG_SHAPE
img_w = tf.cast(img_w, tf.float32)
img_h = tf.cast(img_h, tf.float32)

squared_w = tf.square(img_w)
squared_h = tf.square(img_h)
mask_hw = tf.math.ceil(tf.sqrt(squared_w + squared_h))
mask_hw = tf.cast(mask_hw, tf.int32)

d = tf.random.uniform(
    shape=[batch_size],
    minval=tf.math.minimum(img_h * 0.5, img_w * 0.3),
    maxval=tf.math.maximum(img_h * 0.5, img_w * 0.3) + 1,
)
space = ratio * d

delta_x = tf.random.uniform([batch_size], minval=0, maxval=1, dtype=tf.float32)
delta_y = tf.random.uniform([batch_size], minval=0, maxval=1, dtype=tf.float32)
delta_x = delta_x * space
delta_y = delta_y * space

d = tf.cast(d, tf.int32)

gridsize = mask_hw // d
max_gridsize = tf.reduce_max(gridsize)
gridrange = tf.range(1, max_gridsize + 1)
gridrange = tf.tile(tf.expand_dims(gridrange, 0), [batch_size, 1])

delta_x = tf.expand_dims(tf.cast(delta_x, tf.int32), 1)
delta_y = tf.expand_dims(tf.cast(delta_y, tf.int32), 1)
d = tf.expand_dims(d, 1)
space = tf.expand_dims(tf.cast(space, tf.int32), 1)
square_l = d - space

d_range = gridrange * d
x1 = d_range - delta_x
x0 = x1 - square_l
y1 = d_range - delta_y
y0 = y1 - square_l

# mask ranges
d_range_mask = tf.sequence_mask(gridsize, max_gridsize, tf.int32)
x1 = x1 * d_range_mask
x0 = x0 * d_range_mask
y1 = y1 * d_range_mask
y0 = y0 * d_range_mask
x1

x0 = tf.tile(tf.expand_dims(x0, 1), [1, max_gridsize, 1])
y0 = tf.tile(tf.expand_dims(y0, 1), [1, max_gridsize, 1])
y0 = tf.transpose(y0, [0, 2, 1])

x1 = tf.tile(tf.expand_dims(x1, 1), [1, max_gridsize, 1])
y1 = tf.tile(tf.expand_dims(y1, 1), [1, max_gridsize, 1])
y1 = tf.transpose(y1, [0, 2, 1])

x0 = tf.reshape(x0, [-1, max_gridsize])
y0 = tf.reshape(y0, [-1, max_gridsize])
x1 = tf.reshape(x1, [-1, max_gridsize])
y1 = tf.reshape(y1, [-1, max_gridsize])
x0
y0

corners0 = tf.stack([x0, y0], axis=-1)
corners1 = tf.stack([x1, y1], axis=-1)
corners0 = tf.reshape(corners0, [-1, 2])
corners1 = tf.reshape(corners1, [-1, 2])
corners = tf.concat([corners0, corners1], axis=1)

mask_shape = (tf.shape(corners)[0], mask_hw, mask_hw)
masks = fill_utils.rectangle_masks(mask_shape, corners)
masks = tf.reshape(masks, [-1, max_gridsize * max_gridsize, mask_hw, mask_hw])

hide_mask = tf.reduce_all(corners != 0, axis=1)
hide_mask = tf.reshape(hide_mask, [-1, max_gridsize * max_gridsize])
masks_ = masks & hide_mask[:, :, tf.newaxis, tf.newaxis]

mask = tf.reduce_any(masks, axis=1)
mask_ = tf.reduce_any(masks, axis=1)

# TODO: Rotate mask
# TODO: Center crop mask

for m in mask:
    plt.imshow(m)
    plt.show()

for m in mask_:
    plt.imshow(m)
    plt.show()

# %%
ratio = 0.6

img_h, img_w = 224, 224
img_w = tf.cast(img_w, tf.float32)
img_h = tf.cast(img_h, tf.float32)

squared_w = tf.square(img_w)
squared_h = tf.square(img_h)
mask_hw = tf.math.ceil(tf.sqrt(squared_w + squared_h))
mask_hw = tf.cast(mask_hw, tf.int32)

d = tf.random.uniform(
    shape=[],
    minval=tf.math.minimum(img_h * 0.5, img_w * 0.3),
    maxval=tf.math.maximum(img_h * 0.5, img_w * 0.3) + 1,
)
space = ratio * d

d = tf.cast(d, tf.int32)
space = tf.cast(space, tf.int32)
square_l = d - space

delta_x = tf.random.uniform([], minval=0, maxval=space, dtype=tf.int32)
delta_y = tf.random.uniform([], minval=0, maxval=space, dtype=tf.int32)

gridsize = mask_hw // d + 1
gridrange = tf.range(1, gridsize)
d_range = gridrange * d
x1 = d_range - delta_x
x0 = x1 - square_l
y1 = d_range - delta_y
y0 = y1 - square_l

x0, y0 = tf.meshgrid(x0, y0)
x1, y1 = tf.meshgrid(x1, y1)
corners0 = tf.stack([x0, y0], axis=-1)
corners1 = tf.stack([x1, y1], axis=-1)
corners0 = tf.reshape(corners0, [-1, 2])
corners1 = tf.reshape(corners1, [-1, 2])
corners = tf.concat([corners0, corners1], axis=1)

mask_shape = (tf.shape(corners)[0], mask_hw, mask_hw)
masks = fill_utils.rectangle_masks(mask_shape, corners)
mask = tf.reduce_any(masks, axis=0)

# TODO: Rotate mask
# TODO: Center crop mask

plt.imshow(mask)
plt.show()


#%%
"""
mask2.png
Y
start 51
Num blocks 4
51 101
135 185
219 269
303 353
X
start 72
Num blocks 4
72 122
156 206
240 290
324 374

mask3.png
Y
start 7
Num blocks 5
7 55
87 135
167 215
247 295
327 375
X
start 41
Num blocks 5
41 89
121 169
201 249
281 329
361 403
"""
ratio = 0.6

batch_size, img_h, img_w = tf.shape(img)
img_w = tf.cast(img_w, tf.float32)
img_h = tf.cast(img_h, tf.float32)

mask_hw = 403
mask = tf.zeros((batch_size, mask_hw, mask_hw), dtype=tf.bool)

d = tf.constant([84, 80], tf.float32)
space = ratio * d
space = tf.cast(space, tf.int32)

start_xy = tf.constant(
    [
        [72, 51],  # mask2
        [41, 7],  # mask3
    ]
)

start_xy = tf.cast(start_xy, tf.int32)
d = tf.cast(d, tf.int32)

start_xy
d
space

start_xy


###
gridsize_keep = mask_hw // d
gridsize_mask = gridsize_keep + 1
gridsize_mask
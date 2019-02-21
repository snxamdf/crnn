#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-9-29 下午3:56
# @Author  : Luo Yao
# @Site    : http://github.com/TJCVRS
# @File    : demo_shadownet.py
# @IDE: PyCharm Community Edition
"""
Use shadow net to recognize the scene text
"""
import tensorflow as tf
import os.path as ops
import numpy as np
import cv2
import argparse
import matplotlib.pyplot as plt
try:
    from cv2 import cv2
except ImportError:
    pass

from crnn_model import crnn_model
from global_configuration import config
from local_utils import log_utils, data_utils

logger = log_utils.init_logger()


def init_args() -> argparse.Namespace:
    """

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_path', type=str, help='Where you store the image',
                        default='data/test_images/test_01.jpg')
    parser.add_argument('--weights_path', type=str, help='Where you store the weights',
                        default='model/shadownet/shadownet_2017-09-29-19-16-33.ckpt-39999')
    parser.add_argument('-c', '--num_classes', type=int, default=37,
                        help='Force number of character classes to this number. Set to 0 for auto.')

    return parser.parse_args()


def recognize(image_path: str, weights_path: str, is_vis: bool=True, num_classes: int=0):
    """

    :param image_path:
    :param weights_path:
    :param is_vis:
    :param num_classes:
    """

    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    image = cv2.resize(image, tuple(config.cfg.ARCH.INPUT_SIZE))
    image = np.expand_dims(image, axis=0).astype(np.float32) #增加第一个维度，变成了(1,32,100,3),1就是expand_dims的功劳

    w, h = config.cfg.ARCH.INPUT_SIZE #100，32
    inputdata = tf.placeholder(dtype=tf.float32, shape=[1, h, w, 3], name='input')

    codec = data_utils.TextFeatureIO()
    num_classes = len(codec.reader.char_dict) + 1 if num_classes == 0 else num_classes#这个是在读词表，37个类别，没想清楚？？？为何是37个，26个字母+空格不是37个，噢，对了，还有数字0-9

    net = crnn_model.ShadowNet(phase='Test',
                               hidden_nums=config.cfg.ARCH.HIDDEN_UNITS,
                               layers_nums=config.cfg.ARCH.HIDDEN_LAYERS,
                               num_classes=num_classes)

    with tf.variable_scope('shadow'):
        net_out = net.build_shadownet(inputdata=inputdata)

    decodes, _ = tf.nn.ctc_beam_search_decoder(inputs=net_out, sequence_length=config.cfg.ARCH.SEQ_LENGTH*np.ones(1),
                                               merge_repeated=False)

    # config tf session
    sess_config = tf.ConfigProto()
    sess_config.gpu_options.per_process_gpu_memory_fraction = config.cfg.TRAIN.GPU_MEMORY_FRACTION
    sess_config.gpu_options.allow_growth = config.cfg.TRAIN.TF_ALLOW_GROWTH

    # config tf saver
    saver = tf.train.Saver()

    sess = tf.Session(config=sess_config)

    with sess.as_default():

        saver.restore(sess=sess, save_path=weights_path)

        preds = sess.run(decodes, feed_dict={inputdata: image})
        #将结果，从张量变成字符串数组，session.run(arg)arg是啥类型，就ruturn啥类型
        preds = codec.writer.sparse_tensor_to_str(preds[0])

        logger.info('Predict image {:s} label {:s}'.format(ops.split(image_path)[1], preds[0]))

        if is_vis:
            plt.figure('CRNN Model Demo')
            plt.imshow(cv2.imread(image_path, cv2.IMREAD_COLOR)[:, :, (2, 1, 0)])
            plt.show()

        sess.close()


if __name__ == '__main__':
    args = init_args()
    if not ops.exists(args.image_path):
        raise ValueError('{:s} doesn\'t exist'.format(args.image_path))

    # recognize the image
    recognize(image_path=args.image_path, weights_path=args.weights_path, num_classes=args.num_classes)

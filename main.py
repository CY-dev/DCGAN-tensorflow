import os
from scipy import misc #import scipy.misc
import numpy as np
import glob

from model import DCGAN
from utils.unzip import unzip_and_save
from utils.utils import pp, visualize, to_json, show_all_variables

import tensorflow as tf
from tensorport import get_data_path, get_logs_path


TENSORPORT_USERNAME = "svenchmie"
LOCAL_PATH_TO_LOGS = "checkpoint"
ROOT_PATH_TO_LOCAL_DATA = os.path.expanduser("~/Documents/data")
LOCAL_REPO = "celebA_zipped"


flags = tf.app.flags
flags.DEFINE_integer("epoch", 25, "Epoch to train [25]")
flags.DEFINE_float("learning_rate", 0.0002, "Learning rate of for adam [0.0002]")
flags.DEFINE_float("beta1", 0.5, "Momentum term of adam [0.5]")
flags.DEFINE_integer("train_size", np.inf, "The size of train images [np.inf]")
flags.DEFINE_integer("batch_size", 64, "The size of batch images [64]")
flags.DEFINE_integer("input_height", 108, "The size of image to use (will be center cropped). [108]")
flags.DEFINE_integer("input_width", None, "The size of image to use (will be center cropped). If None, same value as input_height [None]")
flags.DEFINE_integer("output_height", 64, "The size of the output images to produce [64]")
flags.DEFINE_integer("output_width", None, "The size of the output images to produce. If None, same value as output_height [None]")
flags.DEFINE_string("dataset", "celebA", "The name of dataset [celebA, mnist, lsun]")
flags.DEFINE_string("data_path",
    get_data_path(dataset_name = "%s/*" % TENSORPORT_USERNAME,
        local_root = ROOT_PATH_TO_LOCAL_DATA,
        local_repo = LOCAL_REPO,
        path = ""),
    "data path for zip file")
flags.DEFINE_string("checkpoint_dir", get_logs_path(LOCAL_PATH_TO_LOGS), "Directory name to save the checkpoints [checkpoint]")
flags.DEFINE_string("sample_dir", get_logs_path("samples"), "Directory name to save the image samples [samples]") #TODO: replace with os.path.join(logs/samples) when folders are supported
flags.DEFINE_boolean("train", True, "True for training, False for testing [True]")
flags.DEFINE_boolean("crop", True, "True for training, False for testing [True]")
flags.DEFINE_boolean("visualize", False, "True for visualizing, False for nothing [False]")
FLAGS = flags.FLAGS


def main(_):
  print("FLAG1")
  pp.pprint(flags.FLAGS.__flags)

  if FLAGS.input_width is None:
    FLAGS.input_width = FLAGS.input_height
  if FLAGS.output_width is None:
    FLAGS.output_width = FLAGS.output_height

  if not os.path.exists(FLAGS.checkpoint_dir):
    os.makedirs(FLAGS.checkpoint_dir)
  if not os.path.exists(FLAGS.sample_dir):
    os.makedirs(FLAGS.sample_dir)
  #gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.333)
  run_config = tf.ConfigProto()
  run_config.gpu_options.allow_growth=True

  # extract zipfile
  print(FLAGS.dataset)
  print(os.path.join(FLAGS.data_path,"*.zip"))
  source_path = glob.glob(os.path.join(FLAGS.data_path,"*.zip"))
  print(source_path)
  for i, zipped_file in enumerate(source_path):
      print("Extracting image zip %s of %s" % (i+1,len(source_path)))
      if os.path.exists(os.path.join(FLAGS.data_path,"celebA")):
          print("...File already exists")
      else:
          print(zipped_file)
          unzip_and_save(zipped_file, FLAGS.data_path)
          print("...Extracted!")

  print("Reading from %s" % os.path.join(FLAGS.data_path,"*/*.jpg"))
  unzipped_data_path = os.path.join(FLAGS.data_path,"*/*.jpg") #right now we support only one dataset
  print(unzipped_data_path)
  with tf.Session(config=run_config) as sess:
    if FLAGS.dataset == 'mnist':
      dcgan = DCGAN(
          sess,
          input_width=FLAGS.input_width,
          input_height=FLAGS.input_height,
          output_width=FLAGS.output_width,
          output_height=FLAGS.output_height,
          batch_size=FLAGS.batch_size,
          sample_num=FLAGS.batch_size,
          y_dim=10,
          data_path = FLAGS.data_path, #glob signature
          dataset_type=unzipped_data_path,
          crop=FLAGS.crop,
          checkpoint_dir=FLAGS.checkpoint_dir,
          sample_dir=FLAGS.sample_dir)
    else:
      dcgan = DCGAN(
          sess,
          input_width=FLAGS.input_width,
          input_height=FLAGS.input_height,
          output_width=FLAGS.output_width,
          output_height=FLAGS.output_height,
          batch_size=FLAGS.batch_size,
          sample_num=FLAGS.batch_size,
          data_path = unzipped_data_path,
          dataset_type=FLAGS.dataset,
          crop=FLAGS.crop,
          checkpoint_dir=FLAGS.checkpoint_dir,
          sample_dir=FLAGS.sample_dir)

    show_all_variables()

    if FLAGS.train:
      dcgan.train(FLAGS)
    else:
      if not dcgan.load(FLAGS.checkpoint_dir)[0]:
        raise Exception("[!] Train a model first, then run test mode")


    # to_json("./web/js/layers.js", [dcgan.h0_w, dcgan.h0_b, dcgan.g_bn0],
    #                 [dcgan.h1_w, dcgan.h1_b, dcgan.g_bn1],
    #                 [dcgan.h2_w, dcgan.h2_b, dcgan.g_bn2],
    #                 [dcgan.h3_w, dcgan.h3_b, dcgan.g_bn3],
    #                 [dcgan.h4_w, dcgan.h4_b, None])

    # Below is codes for visualization
    OPTION = 1
    visualize(sess, dcgan, FLAGS, OPTION)

if __name__ == '__main__':
  tf.app.run()

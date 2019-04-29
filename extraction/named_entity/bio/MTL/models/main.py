
from __future__ import print_function

import random
from logging import info
import sys

from keras.models import Model
from keras.layers import Input, Embedding, Flatten, Dense, merge
from keras.layers import Reshape, Convolution2D, Dropout

from ltlib import filelog
from ltlib import conlldata
from ltlib import viterbi

from ltlib.features import NormEmbeddingFeature, SennaCapsFeature
from ltlib.features import windowed_inputs
from ltlib.callbacks import token_evaluator, EpochTimer
from ltlib.layers import concat, inputs_and_embeddings
from ltlib.settings import cli_settings, log_settings
from ltlib.optimizers import get_optimizer
from ltlib.output import save_token_predictions

from config import Defaults

config = cli_settings(['datadir', 'wordvecs'], Defaults)

data = conlldata.load_dir(config.datadir, config)

if config.viterbi:
    vmapper = viterbi.TokenPredictionMapper(data.train.sentences)
else:
    vmapper = None

w2v = NormEmbeddingFeature.from_file(config.wordvecs,
                                     max_rank=config.max_vocab_size,
                                     vocabulary=data.vocabulary,
                                     name='words')
features = [w2v]
if config.word_features:
    features.append(SennaCapsFeature(name='caps'))

data.tokens.add_features(features)
data.tokens.add_inputs(windowed_inputs(config.window_size, features))

# Log word vector feature stat summary
info('{}: {}'.format(config.wordvecs, w2v.summary()))

inputs, embeddings = inputs_and_embeddings(features, config)

seq = concat(embeddings)
cshape = (config.window_size, sum(f.output_dim for f in features))

seq_reshape = Reshape(cshape+(1,))(seq)


# Convolutions
conv_outputs = []
for filter_size, filter_num in zip(config.filter_sizes, config.filter_nums):
    conv = Convolution2D(filter_num, filter_size, cshape[1],
                         activation='relu')(seq)
    cout = Flatten()(conv)
    #cout = Reshape((-1, 1))(cout)
    conv_outputs.append(cout)
seq_covout = merge(conv_outputs, mode='concat', concat_axis=-1)




for size in config.hidden_sizes:
    seq_2 = Dense(size, activation=config.hidden_activation)(seq_covout)
seq_3 = Dropout(config.output_drop_prob)(seq_2)
out = Dense(data.tokens.target_dim, activation='softmax')(seq_3)
model = Model(input=inputs, output=out)


optimizer = get_optimizer(config)
model.compile(loss='categorical_crossentropy', optimizer=optimizer,
              metrics=['accuracy'])

callbacks = [
    EpochTimer(),
    #token_evaluator(data.train, mapper=vmapper, config=config),
    #token_evaluator(data.test, mapper=vmapper, config=config),
]

percnt_keep = config.percent_keep
amt_keep = len(data.train.tokens.inputs['words']) * percnt_keep
print("Total: %s. Keeping: %s" % (len(data.train.tokens.inputs['words']), amt_keep))
start = random.randrange(int(len(data.train.tokens.inputs['words']) - amt_keep + 1))
end = int(start + amt_keep)
x = data.train.tokens.inputs['words'][start:end]


model.fit(
    #data.train.tokens.inputs,
    x,
    data.train.tokens.targets[start:end],
    callbacks=callbacks,
    batch_size=config.batch_size,
    nb_epoch=1,
    verbose=1
)


# In[49]:

name = "chemdner_output"
save_token_predictions(name, data.test, model, conlldata.write)



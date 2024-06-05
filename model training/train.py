import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import Callback, ModelCheckpoint
import tensorflow.keras.backend as K

# Define paths to the dataset
train_dir = '/content/drive/MyDrive/dataset split7/train'
val_dir = '/content/drive/MyDrive/dataset split7/val'
test_dir = '/content/drive/MyDrive/dataset split7/test'

# Define parameters
batch_size = 32
num_classes = 10

# Create data generators
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)
val_datagen = ImageDataGenerator(rescale=1./255)
test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode='categorical'
)
val_generator = val_datagen.flow_from_directory(
    val_dir,
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode='categorical'
)
test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode='categorical'
)

# Load MobileNetV2 model without the top (classification) layer
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Add custom classification head with dropout
x = GlobalAveragePooling2D()(base_model.output)
x = Dense(1024, activation='relu')(x)
x = Dropout(0.5)(x)
predictions = Dense(num_classes, activation='softmax')(x)

# Create the model
model = Model(inputs=base_model.input, outputs=predictions)

# Freeze the base model layers
for layer in base_model.layers:
    layer.trainable = False

# Class weights
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_generator.classes),
    y=train_generator.classes
)
class_weight_dict = {i: class_weights[i] for i in range(len(class_weights))}

# Cyclical Learning Rate Scheduler
class CyclicalLearningRate(Callback):
    def __init__(self, base_lr=0.0001, max_lr=0.001, step_size=2000., scale_fn=None, scale_mode='cycle'):
        super(CyclicalLearningRate, self).__init__()
        self.base_lr = base_lr
        self.max_lr = max_lr
        self.step_size = step_size
        self.scale_mode = scale_mode
        self.scale_fn = scale_fn or self.scale_function
        self.clr_iterations = 0.

    def scale_function(self, x):
        return 1 / (5.**(x - 1))

    def clr(self):
        cycle = math.floor(1 + self.clr_iterations / (2 * self.step_size))
        x = abs(self.clr_iterations / self.step_size - 2 * cycle + 1)
        return self.base_lr + (self.max_lr - self.base_lr) * max(0, (1 - x)) * self.scale_fn(cycle)

    def on_train_begin(self, logs=None):
        logs = logs or {}
        K.set_value(self.model.optimizer.lr, self.base_lr)

    def on_train_batch_end(self, batch, logs=None):
        logs = logs or {}
        self.clr_iterations += 1
        K.set_value(self.model.optimizer.lr, self.clr())


clr = CyclicalLearningRate(base_lr=0.0001, max_lr=0.001, step_size=2000.)

# Model Checkpoint to save the best model based on validation accuracy
checkpoint_filepath = '/content/drive/MyDrive/models/best_model.h5'
model_checkpoint_callback = ModelCheckpoint(
    filepath=checkpoint_filepath,
    save_weights_only=False,
    monitor='val_accuracy',
    mode='max',
    save_best_only=True,
    verbose=1
)

# Compile the model
model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model with Cyclical Learning Rate and ModelCheckpoint
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    epochs=35,
    validation_data=val_generator,
    validation_steps=val_generator.samples // batch_size,
    class_weight=class_weight_dict,
    callbacks=[clr, model_checkpoint_callback]
)

# Load the best model before final evaluation or deployment
model.load_weights(checkpoint_filepath)

# Evaluate the model on the test set
test_loss, test_accuracy = model.evaluate(test_generator)
print("Test accuracy:", test_accuracy)

# Save the model with accuracy in the filename
accuracy_label = "{:0.2f}".format(test_accuracy * 100)
model_save_path = f'/content/drive/My Drive/models/mobilenetv2_acc_{accuracy_label}.h5'
model.save(model_save_path)

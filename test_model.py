import torch
from torchvision import models

MODEL_PATH = "model/best_lung_cancer_resnet18.pth"

CLASS_NAMES = [
    "Bengin cases",
    "Malignant cases",
    "Normal cases"
]

print("=" * 60)
print("TESTING LUNG CANCER MODEL")
print("=" * 60)

print("\nLoading ResNet18...")

# Create ResNet18 architecture
model = models.resnet18(weights=None)

# Change final layer to match number of classes
num_features = model.fc.in_features

model.fc = torch.nn.Linear(
    num_features,
    len(CLASS_NAMES)
)

# Load checkpoint
checkpoint = torch.load(
    MODEL_PATH,
    map_location="cpu"
)

# Load only the trained model weights
model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

print("Model loaded successfully!")
print()

# Display classes
print("Classes:")
for i, name in enumerate(CLASS_NAMES):
    print(f"{i} -> {name}")

print()

# Optional: display information saved in checkpoint
if "best_epoch" in checkpoint:
    print("Best Epoch:", checkpoint["best_epoch"])

if "best_val_loss" in checkpoint:
    print("Best Validation Loss:", checkpoint["best_val_loss"])

print()
print("Model is ready for prediction.")
print("=" * 60)
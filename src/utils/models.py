from pathlib import Path
from typing import Dict

import kaggle  # type: ignore
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from torchvision import models  # type: ignore


class Models:
    def __init__(self) -> None:
        kaggle.api.authenticate()
        self.root_folder = Path(__file__).parent.parent.parent
        self.download_folder = self.root_folder / "data" / "models"
        self.size_tuple = (224, 224)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_weights: Dict[str, float] = dict()

    def download_from_kaggle(self) -> None:
        self.download_folder.mkdir(exist_ok=True)
        kaggle.api.dataset_download_files(  # type: ignore
            "dzmitrypihulski/models-for-hackathon",
            path=self.download_folder,
            unzip=True,
            quiet=False,
        )

    def create_new_efficientnet_b0(self, num_classes: int = 8) -> nn.Module:
        model = models.efficientnet_b0(weights="DEFAULT")
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        return model.to(self.device)

    def create_new_efficientnet_b1(self, num_classes: int = 8) -> nn.Module:
        model = models.efficientnet_b1(weights="IMAGENET1K_V2")
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        return model.to(self.device)

    def create_new_mobilenet_v3_large(self, num_classes: int = 8) -> nn.Module:
        model = models.mobilenet_v3_large(weights="IMAGENET1K_V2")
        model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
        return model.to(self.device)

    def create_new_shufflenet_v2_x2_0(self, num_classes: int = 8) -> nn.Module:
        model = models.shufflenet_v2_x2_0(weights="DEFAULT")
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model.to(self.device)

    def prepare_finetuned_efficientnet_b0(
        self, model_name: str, num_classes: int = 8
    ) -> nn.Module:
        model = models.efficientnet_b0(weights="DEFAULT")
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

        checkpoint = torch.load(  # type: ignore
            str(self.download_folder) + f"/{model_name}_best_f1.pth"
        )

        model.load_state_dict(checkpoint["model_state_dict"])

        model.eval()
        self.model_weights[model_name] = checkpoint["best_val_f1"]
        return model.to(self.device)

    def prepare_finetuned_efficientnet_b1(
        self, model_name: str, num_classes: int = 8
    ) -> nn.Module:
        model = models.efficientnet_b1(weights="IMAGENET1K_V2")
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

        checkpoint = torch.load(  # type: ignore
            str(self.download_folder) + f"/{model_name}_best_f1.pth"
        )

        model.load_state_dict(checkpoint["model_state_dict"])

        model.eval()
        self.model_weights[model_name] = checkpoint["best_val_f1"]
        return model.to(self.device)

    def prepare_finetuned_mobilenet_v3_large(
        self, model_name: str, num_classes: int = 8
    ) -> nn.Module:
        model = models.mobilenet_v3_large(weights="IMAGENET1K_V2")
        model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)

        checkpoint = torch.load(  # type: ignore
            str(self.download_folder) + f"/{model_name}_best_f1.pth"
        )

        model.load_state_dict(checkpoint["model_state_dict"])

        model.eval()
        self.model_weights[model_name] = checkpoint["best_val_f1"]

        return model.to(self.device)

    def prepare_finetuned_shufflenet_v2_x2_0(
        self, model_name: str, num_classes: int = 8
    ) -> nn.Module:
        model = models.shufflenet_v2_x2_0(weights="DEFAULT")
        model.fc = nn.Linear(model.fc.in_features, num_classes)

        checkpoint = torch.load(  # type: ignore
            str(self.download_folder) + f"/{model_name}_best_f1.pth"
        )

        model.load_state_dict(checkpoint["model_state_dict"])

        model.eval()
        self.model_weights[model_name] = checkpoint["best_val_f1"]

        return model.to(self.device)

    def plot_training_metrics(self, checkpoint_path: str, name_of_the_net: str) -> None:
        checkpoint = torch.load(checkpoint_path)  # type: ignore
        losses_val = checkpoint["val_loss"]
        losses_train = checkpoint["train_loss"]
        f1_metric_val = checkpoint["f1_metric_val"]

        plt.figure(figsize=(10, 7))  # type: ignore

        # Create the first plot with the left y-axis
        fig, ax1 = plt.subplots(figsize=(10, 7))  # type: ignore

        # Plot train and validation loss on the left y-axis
        ax1.plot(  # type: ignore
            np.arange(1, len(losses_train) + 1),  # type: ignore
            losses_train,
            color="r",
            label="Train loss",
        )
        ax1.plot(  # type: ignore
            np.arange(1, len(losses_val) + 1),  # type: ignore
            losses_val,
            "-g",
            # "-gD",
            label="Val loss",
            # markevery=marker_on,
        )

        ax1.set_xlabel("Epoch")  # type: ignore
        ax1.set_ylabel("CrossEntropyLoss")  # type: ignore
        ax1.grid()  # type: ignore

        # Create the second y-axis for F1 metric
        marker_on = [f1_metric_val.index(max(f1_metric_val))]
        ax2 = ax1.twinx()
        ax2.plot(  # type: ignore
            np.arange(1, len(f1_metric_val) + 1),  # type: ignore
            f1_metric_val,
            "-bD",
            label="F1 Metric (Val)",
            markevery=marker_on,
        )
        ax2.set_ylabel("f1_metric_val")  # type: ignore

        # Annotate the minimum loss point
        bbox = dict(boxstyle="round", fc="0.8")
        ax2.annotate(  # type: ignore
            text=f"Max F1 score after {f1_metric_val.index(max(f1_metric_val))+1} epochs, equals: {round(max(f1_metric_val), 3)}",
            xy=(
                f1_metric_val.index(max(f1_metric_val)) + 1,
                max(f1_metric_val),
            ),
            xytext=(
                f1_metric_val.index(max(f1_metric_val)) + 1,
                max(f1_metric_val) - 0.015,
            ),
            arrowprops=dict(
                facecolor="gray", shrink=0.1, connectionstyle="arc3,rad=0.3"
            ),
            bbox=bbox,
            ha="right",
            va="center",
        )

        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")  # type: ignore
        ax2.set_ylim(ymax=(max(f1_metric_val) * 1.015))

        plt.title(  # type: ignore
            f"{name_of_the_net} - Train and Val loss, F1 Metric after {len(losses_train)} epochs"
        )  # type: ignore
        plt.savefig(str(self.root_folder) + f"/data/images/{name_of_the_net}.png")  # type: ignore

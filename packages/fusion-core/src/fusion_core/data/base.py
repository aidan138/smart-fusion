from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any 

import torch
from torch import Tensor
from torch.utils.data import Dataset as TorchDataset

@dataclass
class MultimodalSample:
    """
    The unified unit every adapter must produce and every model must consume.

    modalities: keys are modality names ("audio", "text", "video", ...).
                Values are already-transformed tensors, ready for the encoder.
                No raw/untransformed data should reach this stage.
    label:      target tensor. Shape/dtype depends on task (classification,
                regression, multi-label) but must be consistent within a dataset.
    meta:       anything useful for debugging/analysis that is NOT fed to the
                model — sample id, dataset name, split, original length, etc.
    """
    modalities: dict[str, Tensor]
    label: Tensor
    meta: dict[str, Any] = field(default_factory=dict)

    def to(self, device: torch.device) -> "MultimodalSample":
        """Move all tensors to target device, leave meta untouched."""
        return MultimodalSample(
            modalities={name: tensor.to(device) for name, tensor in self.modalities.items()},
            label=self.label.to(device),
            meta=self.meta
        )



class MultimodalDataset(TorchDataset, ABC):
    """
    Abstract base every dataset adapter must subclass. Inheriting from
    torch.utils.data.Dataset means adapters drop straight into a DataLoader,
    but the abstract methods below are what make them interchangeable with
    each other from the training loop's point of view.
    """
     
    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __getitem__(self):
        ...

    @property
    @abstractmethod
    def modality_shapes(self) -> dict[str, tuple[int, ...]]:
        ...

    @property
    @abstractmethod
    def modalities(self) -> list[str]:
        ...

    @property
    def name(self) -> str:
        return self.__class__.__name__

class MultimodalRegistry:
    """
    Central lookup so config files can reference datasets by string name
    (e.g. dataset=mosei in Hydra) without fusion-core importing fusion-datasets.
    fusion-datasets/__init__.py populates this at import time.
    """
    # type indicates it stores class types not class object instances
    _registry: dict[str, type[MultimodalDataset]] = {} 

    @classmethod
    def register(cls, name: str):
        def decorator(dataset_cls: MultimodalDataset):
            if name in cls._registry:
                raise ValueError(f"Dataset '{name} already registered.")
            cls._registry[name] = dataset_cls
            return dataset_cls

        return decorator

    @classmethod
    def get(cls, name) -> type[MultimodalDataset]:
        if name not in cls._registry:
            raise KeyError(
                f"Dataset '{name}' not found. Registered: {list(cls._registry)}"
            )
        return cls._registry[name]

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._registry.keys())


import torch

print("Pytorch:", torch.__version__)
print("Built with CUDA", torch.version.cuda)
print("CUDA available:", torch.cuda.is_available())

if not torch.cuda.is_available():
    raise RuntimeError("Pytorch cannot access the GPU")

print("GPU:", torch.cuda.get_device_name(0))

print(
    "VRAM:",
    round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2),
    "GiB"
)

x = torch.randn(4096, 4096, device="cuda")
y = x @ x
torch.cuda.synchronize()

print("Matrix multiplication succeeded:", y.shape)
print(
    "Allocated:",
    round(torch.cuda.memory_allocated() / 1024**2, 2),
    "MiB",
)

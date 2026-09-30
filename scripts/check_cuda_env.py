import sys
import torch

def main():
    print(f"Python: {sys.version}")
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"Device name: {torch.cuda.get_device_name(0)}")
        print(f"Compute capability: {torch.cuda.get_device_capability(0)}")
        
        # Test basic tensor operation on GPU
        x = torch.tensor([1.0, 2.0, 3.0], device="cuda", dtype=torch.float64)
        y = x * 2.0 + 1.0
        print(f"GPU tensor test: y = {y.cpu().numpy()}")

        # Test sparse tensor support on GPU
        i = torch.tensor([[0, 1, 1], [2, 0, 2]], dtype=torch.long)
        v = torch.tensor([3.0, 4.0, 5.0], dtype=torch.float64)
        s = torch.sparse_coo_tensor(i, v, (2, 3), device="cuda")
        print("GPU Sparse COO tensor created successfully:")
        print(s)

if __name__ == "__main__":
    main()

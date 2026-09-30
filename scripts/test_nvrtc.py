import ctypes
import os
import sys

# Find cuda dlls
import torch

def test_nvrtc():
    print("Testing NVRTC compilation and execution...")
    # Load cuda driver and nvrtc
    try:
        from cuda import cuda, nvrtc
        print("cuda-python package found!")
        return True
    except ImportError:
        pass

    # Use ctypes to load nvrtc and nvcuda
    try:
        # CUDA driver API via ctypes
        nvcuda = ctypes.CDLL("nvcuda.dll")
        print("Loaded nvcuda.dll successfully!")
    except Exception as e:
        print("Failed to load nvcuda.dll:", e)
        return False

    # Check NVRTC DLL
    nvrtc_dll = None
    cuda_path = os.environ.get("CUDA_PATH", "D:/CUDA")
    candidates = [
        "nvrtc64_120_0.dll", "nvrtc64_121_0.dll", "nvrtc64_122_0.dll",
        "nvrtc64_126_0.dll", "nvrtc.dll",
        os.path.join(cuda_path, "bin", "nvrtc64_120_0.dll"),
        os.path.join(cuda_path, "bin", "nvrtc64_126_0.dll"),
    ]
    for c in candidates:
        if os.path.exists(c):
            nvrtc_dll = c
            break
        try:
            ctypes.CDLL(c)
            nvrtc_dll = c
            break
        except Exception:
            continue
    
    print(f"NVRTC DLL candidate: {nvrtc_dll}")
    return True

if __name__ == "__main__":
    test_nvrtc()

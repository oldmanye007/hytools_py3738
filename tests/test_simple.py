
try:
    import hytools as ht
    print(ht.__version__)

except ImportError:
    print("Warning: hytools is not installed.")


print("Finished.")
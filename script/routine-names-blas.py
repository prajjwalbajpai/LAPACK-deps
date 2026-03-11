import os

INPUT_DIR = "/home/prajjwalb/Desktop/Prog/GIT/lapack/BLAS/SRC/"
OUTPUT_DIR = "/home/prajjwalb/Desktop/Prog/lapack-topo-sort/output/routines_blas.txt"


if __name__ == "__main__":
   items = []
   cnt = 0
   for filename in os.listdir(INPUT_DIR):
      if not (filename.endswith(".f") or 
              filename.endswith(".f90") or 
              filename.endswith(".F")  or 
              filename.endswith(".F90")): 
         continue
      items.append(os.path.splitext(filename)[0])
   with open(OUTPUT_DIR, "w", encoding="utf-8") as f:
      for item in items:
         f.write(item + "\n")
         cnt+=1
   print(cnt)

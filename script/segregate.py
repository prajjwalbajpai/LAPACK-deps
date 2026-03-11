#!/usr/bin/env python3

# ------------------ hardcoded paths ------------------
INPUT_TXT = "output/topo_order.txt"

SINGLE_PRECISION_COMPLEX = "output/SINGLE_PRECISION_COMPLEX.txt"
DOUBLE_PRECISION = "output/DOUBLE_PRECISION.txt"
DOUBLE_PRECISION_COMPLEX = "output/DOUBLE_PRECISION_COMPLEX.txt"
SINGLE_PRECISION = "output/SINGLE_PRECISION.txt"
OTHERS = "output/OTHERS.txt"
# -----------------------------------------------------

def segregate_routines():
	with open(INPUT_TXT, "r", encoding="utf-8") as f:
		routines = [line.strip() for line in f if line.strip()]

	spc = []
	dp = []
	dpc = []
	sp = []
	others = []

	for r in routines:
		first = r[0].lower()

		if first == "c":
			spc.append(r)
		elif first == "d":
			dp.append(r)
		elif first == "z":
			dpc.append(r)
		elif first == "s":
			sp.append(r)
		else:
			others.append(r)

	def write(path, data):
		with open(path, "w", encoding="utf-8") as f:
			for x in data:
					f.write(x + "\n")

	write(SINGLE_PRECISION_COMPLEX, spc)
	write(DOUBLE_PRECISION, dp)
	write(DOUBLE_PRECISION_COMPLEX, dpc)
	write(SINGLE_PRECISION, sp)
	write(OTHERS, others)

	print("Segregation complete.")
	print(f"c  -> {len(spc)}")
	print(f"d  -> {len(dp)}")
	print(f"z  -> {len(dpc)}")
	print(f"s  -> {len(sp)}")
	print(f"others -> {len(others)}")


if __name__ == "__main__":
	segregate_routines()

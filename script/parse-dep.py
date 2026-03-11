import pathlib
import string
import json
import os


EXTS = ['.f', '.F', '.f90']

def get_routine_path(path, routine):
	for ext in EXTS:
		file_path = os.path.join(path, routine + ext)
		if os.path.isfile(file_path):
			return file_path
	return None  # not found

translator = str.maketrans('', '', string.punctuation)
PATH = '/home/prajjwalb/Desktop/Prog/GIT/lapack/SRC/'
def parse_file( lapk : set[str], blas : set[str], routine: str ):
	deps_lapk = set()
	deps_blas = set()
	file_path = get_routine_path(PATH, routine)
	if(file_path == None):
		print("routine no found : ", routine)
		return deps_blas, deps_lapk
	
	with open(file_path, "r") as f:
		for line in f:
			if line.startswith('*'): 
				continue

			for w in line.split(): 
				if('(' not in w): continue
				# print(w)
				w_arr = w.split('(')
				for word in w_arr:
					word = word.lower().translate(translator)
					# print(word)
					if word == routine:
						continue
					if word in lapk:
						# print(line, word)
						deps_lapk.add(word)
					elif word in blas:
						deps_blas.add(word)
	return deps_blas, deps_lapk

if __name__ == "__main__":
	# path = '/home/prajjwalb/Desktop/Prog/GIT/lapack/SRC/dsytrs2.f'
	known_lapk = {x.strip().lower()
				for x in pathlib.Path('output/routines.txt').read_text().split() if x.strip()}
	known_blas = {x.strip().lower()
				for x in pathlib.Path('output/routines_blas.txt').read_text().split() if x.strip()}
	blas_dep = dict()
	lapk_dep = dict()

	blas, lapk = parse_file(known_lapk, known_blas, 'disnan')

	for routine in known_lapk:
		# routine = 'dlartgp'
		blas, lapk = parse_file(known_lapk, known_blas, routine)
		blas = sorted(blas)
		lapk = sorted(lapk)
		blas_dep[routine] = blas
		lapk_dep[routine] = lapk

	

	with open('output/graph.json', "w", encoding="utf-8") as f:
		json.dump(lapk_dep, f, indent=2, ensure_ascii=False)

	with open('output/graph_blas.json', "w", encoding="utf-8") as f:
		json.dump(blas_dep, f, indent=2, ensure_ascii=False)

	
	print('Wrote', len(blas_dep) ,'routines to blas!')
	print('Wrote', len(lapk_dep) ,'routines to lapk!')

	# print(blas_dep)
	# print(lapk_dep)



	

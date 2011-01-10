## {{{ http://code.activestate.com/recipes/527746/ (r1)
import os
import fnmatch

def Walk(root='.', recurse=True, pattern='*'):
    """
        Generator for walking a directory tree.
        Starts at specified root folder, returning files
        that match our pattern. Optionally will also
        recurse through sub-folders.
    """
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                yield os.path.join(path, name)
        if not recurse:
            break

def LOC(root='', recurse=True):
    """
        Counts lines of code in two ways:
            maximal size (source LOC) with blank lines and comments
            minimal size (logical LOC) stripping same

        Sums all Python files in the specified folder.
        By default recurses through subfolders.
    """
    count_mini, count_maxi = 0, 0
    for fspec in Walk(root, recurse, '*.py'):
        skip = False
        for line in open(fspec).readlines():
            count_maxi += 1
            
            line = line.strip()
            if line:
                if line.startswith('#'):
                    continue
                if line.startswith('"""'):
                    skip = not skip
                    continue
                if not skip:
                    count_mini += 1

    return count_mini, count_maxi
## end of http://code.activestate.com/recipes/527746/ }}}

if __name__ == "__main__":
    min1, max1 = LOC(root="xVClient")
    min2, max2 = LOC(root="xVLib")
    min3, max3 = LOC(root="xVMapEdit")
    min4, max4 = LOC(root="xVServer")
    min = min1 + min2 + min3 + min4
    max = max1 + max2 + max3 + max4
    print "without comments + whitespace: ", min
    print "with comments + whitespace: ", max

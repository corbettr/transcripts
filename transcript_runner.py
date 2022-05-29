""" Terminal runner for transcripts.py """
import sys
from transcripts import *

def main():
    if len(sys.argv) <= 1:
        sys.exit("Usage: python transcript_runner.py 'Transcripts.pdf' ")

    input_file = sys.argv[1]
    # print(input_file)
    
    if len(sys.argv) == 2:
        print("Analyzing transcripts...")
        analyze_transcripts(input_file)
        print("All done!")
        
    if len(sys.argv) > 3:
        print("Warning: Using only first two arguments.")
        
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
        print("Analyzing transcripts...")
        analyze_transcripts(input_file, output_file)
        print("All done!")


if __name__ == "__main__":
    main()

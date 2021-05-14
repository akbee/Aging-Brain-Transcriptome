import os
import time
from shutil import copy2
## This file will walk through the basic steps of preprocessing the fastq files following downloading from NCBI#
def fastqc_report(input_fastq):
    """creates a fastqc report"""
    try:
        output_dir = "Fastqc_{}".format(str(input_fastq).replace(".fastq",""))
        clean_fastq = "Trimmed_" + str(input_fastq)
        os.system("fastqc -o {} -t 8 --nogroup {} {}".format(output_dir, input_fastq, clean_fastq))
        print("FastQC successfully processed {}.\n".format(input_fastq))
    except:
        print("An error occurred during the FastQC for {}".format(input_fastq))
        return None


def trim_reads(input_fastq):
    """ trimms the adapter reads from the fastq files"""
    try:
        trimmed_file_name = "Trimmed_" + str(input_fastq)
        os.system("bbduk.sh in={} out={} ref=./bbmap/resources/polyA.fa.gz, ./bbmap/resources/truseq.fa.gz k=13 ktrim=r useshortkmers=t, mink=5 qtrim=r trimq=10 minlength=20".format(input_fastq, trimmed_file_name))
        print("BBDUK successfully removed adapters from {}.\n".format(input_fastq))
        return trimmed_file_name

    except:
        print("An error occurred during the BBDUK Adapter removal for {}".format(input_fastq))
        return None


def align_to_genome(clean_fastq):
    try:
        bam_file = "starAligned.sortedByCoord.out.bam"
        os.system("STAR --runThreadN 8 --genomeDir genome --readFilesIn {} --outFilterType BySJout --outFilterMultimapNmax 20 --alignSJoverhangMin 8 --alignSJDBoverhangMin 1 --outFilterMismatchNmax 999 --outFilterMismatchNoverLmax 0.6 --alignIntronMin 20 --alignIntronMax 1000000 --alignMatesGapMax 1000000 --outSAMattributes NH HI NM MD --genecounts --outSAMtype BAM SortedByCoordinate --outFileNamePrefix {} ".format(clean_fastq, clean_fastq))
        return bam_file
    except:
        print("An error occurred during the STAR Alignment to the genome removal for {}".format(input_fastq))
        return None


def read_indexing(bam_file, input_fastq):
    """use sam tools to read index the bam file"""
    try:
        os.system("samtools index {}".format(bam_file))
    except:
        print("An error occurred during the samtools indexing for {}".format(input_fastq))


def get_read_counts(bam_file, input_fastq):
    """ use htseq to align reads to genome"""
    try:
        os.system("htseq-count -m intersection-nonempty -s yes -f bam -r pos {} ./genome/rn6.gtf > read_counts.txt".format(bam_file))
        print("htseq successfully counted reads from {}.\n".format(input_fastq))
    except:
        print("An error occurred during the htseq Read Counting for {}".format(input_fastq))
        return None



def main():
    root_dir = os.getcwd()
    for file in os.listdir():
        if file.endswith("fastq.gz"):
            try:
                start_time = time.time()
                #make a folder & move into it
                name_of_dir = str(file).replace("fastq.gz","")
                os.mkdir(name_of_dir)
                os.chdir(name_of_dir)
                copy2(file, os.path.join(name_of_dir, file))
                #gunzip the file
                if file.endswith(".gz"):
                    os.system("gunzip {}".format(file))
                else:
                    pass
                #run fastqc
                fastqc_report(file)
                #use bbduk to remove adapters
                trimmed_file_name = trim_reads(file)
                #run fastq again
                fastqc_report(trimmed_file_name)
                #USE STAR to align to the genome
                bam_file = align_to_genome(trimmed_file_name)
                #use samtools to index the bam file
                read_indexing(bam_file)
                #use htseq-count to create our read counts
                elapsed_time = time.time() - start_time
                os.chdir("..")
                print("finished processing {} --- time required was: ".format(file, elapsed_time))
            except:
                print("Something went wrong with {}".format(file))
                os.chdir(root_dir)
        else:
            pass


if __name__ == '__main__':
    main()

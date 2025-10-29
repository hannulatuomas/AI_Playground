Here's the result of running `cat -n` on /home/ubuntu/ai-agent-console/agents/languages/shell/best_practices.md:
     1	
     2	# Bash/Zsh/Sh Best Practices
     3	
     4	## Code Organization and Structure
     5	
     6	### Script Structure
     7	```bash
     8	#!/usr/bin/env bash
     9	#
    10	# Script Name: backup_database.sh
    11	# Description: Backs up PostgreSQL database to S3
    12	# Author: Your Name
    13	# Date: 2024-01-01
    14	# Version: 1.0.0
    15	#
    16	# Usage: ./backup_database.sh [database_name]
    17	#
    18	# Dependencies: aws-cli, postgresql-client
    19	#
    20	
    21	# Exit on error, undefined variables, and pipe failures
    22	set -euo pipefail
    23	
    24	# Set IFS to default (space, tab, newline)
    25	IFS=$' \t\n'
    26	
    27	# Script directory
    28	SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    29	
    30	# Configuration
    31	readonly CONFIG_FILE="${SCRIPT_DIR}/config.conf"
    32	readonly LOG_FILE="/var/log/backup.log"
    33	
    34	# Source configuration
    35	if [[ -f "${CONFIG_FILE}" ]]; then
    36	    source "${CONFIG_FILE}"
    37	fi
    38	
    39	# Functions
    40	log() {
    41	    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
    42	}
    43	
    44	error() {
    45	    echo "[ERROR] $*" >&2
    46	    exit 1
    47	}
    48	
    49	cleanup() {
    50	    # Cleanup code here
    51	    log "Cleaning up..."
    52	}
    53	
    54	# Set trap for cleanup
    55	trap cleanup EXIT INT TERM
    56	
    57	main() {
    58	    # Main logic here
    59	    log "Starting backup..."
    60	}
    61	
    62	# Run main function
    63	main "$@"
    64	```
    65	
    66	### Project Organization
    67	```
    68	project/
    69	├── bin/                    # Executable scripts
    70	│   ├── deploy.sh
    71	│   └── start.sh
    72	├── lib/                    # Library/function files
    73	│   ├── common.sh
    74	│   └── utils.sh
    75	├── config/                 # Configuration files
    76	│   ├── dev.conf
    77	│   └── prod.conf
    78	├── tests/                  # Test scripts
    79	│   ├── test_common.sh
    80	│   └── run_tests.sh
    81	├── docs/                   # Documentation
    82	├── .shellcheckrc          # ShellCheck config
    83	└── README.md
    84	```
    85	
    86	### Sourcing Libraries
    87	```bash
    88	# Source library files
    89	SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    90	source "${SCRIPT_DIR}/../lib/common.sh" || {
    91	    echo "Failed to source common.sh" >&2
    92	    exit 1
    93	}
    94	
    95	# Or with error handling
    96	source_lib() {
    97	    local lib_file="$1"
    98	    if [[ -f "${lib_file}" ]]; then
    99	        source "${lib_file}"
   100	    else
   101	        echo "Error: Library file ${lib_file} not found" >&2
   102	        return 1
   103	    fi
   104	}
   105	```
   106	
   107	## Naming Conventions
   108	
   109	### Variables
   110	```bash
   111	# Constants: UPPER_CASE
   112	readonly MAX_RETRIES=3
   113	readonly API_URL="https://api.example.com"
   114	readonly DEFAULT_TIMEOUT=30
   115	
   116	# Global variables: UPPER_CASE (but avoid if possible)
   117	GLOBAL_COUNTER=0
   118	
   119	# Local variables: lowercase_with_underscores
   120	local user_name="john"
   121	local file_count=0
   122	
   123	# Environment variables: UPPER_CASE
   124	export PATH="/usr/local/bin:${PATH}"
   125	export DATABASE_URL="postgresql://localhost/mydb"
   126	
   127	# Private/internal variables: prefix with underscore
   128	_internal_cache=""
   129	```
   130	
   131	### Functions
   132	```bash
   133	# Function names: lowercase_with_underscores
   134	get_user_data() {
   135	    local user_id="$1"
   136	    # Implementation
   137	}
   138	
   139	# Private functions: prefix with underscore
   140	_validate_input() {
   141	    # Internal validation
   142	}
   143	
   144	# Boolean-returning functions: use is_ or has_ prefix
   145	is_valid_email() {
   146	    local email="$1"
   147	    [[ "${email}" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]
   148	}
   149	
   150	has_command() {
   151	    command -v "$1" &> /dev/null
   152	}
   153	```
   154	
   155	### Files
   156	```bash
   157	# Script files: lowercase with .sh extension
   158	backup_database.sh
   159	deploy_app.sh
   160	
   161	# Library files: lowercase with .sh extension
   162	common.sh
   163	utils.sh
   164	
   165	# Configuration files: .conf or .config
   166	app.conf
   167	database.config
   168	```
   169	
   170	## Error Handling Patterns
   171	
   172	### Exit on Error
   173	```bash
   174	# Enable strict error handling
   175	set -e          # Exit on error
   176	set -u          # Exit on undefined variable
   177	set -o pipefail # Exit on pipe failure
   178	
   179	# Combine them
   180	set -euo pipefail
   181	
   182	# Disable temporarily if needed
   183	set +e
   184	command_that_might_fail
   185	exit_code=$?
   186	set -e
   187	
   188	if [[ ${exit_code} -ne 0 ]]; then
   189	    echo "Command failed with exit code ${exit_code}"
   190	fi
   191	```
   192	
   193	### Error Checking
   194	```bash
   195	# Check command success
   196	if ! command -v docker &> /dev/null; then
   197	    echo "Error: docker is not installed" >&2
   198	    exit 1
   199	fi
   200	
   201	# Check file existence
   202	if [[ ! -f "${CONFIG_FILE}" ]]; then
   203	    echo "Error: Config file ${CONFIG_FILE} not found" >&2
   204	    exit 1
   205	fi
   206	
   207	# Check directory existence
   208	if [[ ! -d "${DATA_DIR}" ]]; then
   209	    mkdir -p "${DATA_DIR}" || {
   210	        echo "Error: Failed to create directory ${DATA_DIR}" >&2
   211	        exit 1
   212	    }
   213	fi
   214	
   215	# Check exit codes
   216	if ! curl -f "${API_URL}"; then
   217	    echo "Error: Failed to fetch data from ${API_URL}" >&2
   218	    exit 1
   219	fi
   220	
   221	# Or store exit code
   222	curl -f "${API_URL}"
   223	exit_code=$?
   224	if [[ ${exit_code} -ne 0 ]]; then
   225	    echo "curl failed with exit code ${exit_code}" >&2
   226	    exit 1
   227	fi
   228	```
   229	
   230	### Trap for Cleanup
   231	```bash
   232	# Cleanup function
   233	cleanup() {
   234	    local exit_code=$?
   235	    echo "Cleaning up..."
   236	    
   237	    # Remove temporary files
   238	    rm -f "${TEMP_FILE}" 2>/dev/null
   239	    
   240	    # Kill background processes
   241	    if [[ -n "${BACKGROUND_PID:-}" ]]; then
   242	        kill "${BACKGROUND_PID}" 2>/dev/null
   243	    fi
   244	    
   245	    exit "${exit_code}"
   246	}
   247	
   248	# Set trap
   249	trap cleanup EXIT INT TERM
   250	
   251	# Create temp file
   252	TEMP_FILE="$(mktemp)"
   253	
   254	# Your script logic here
   255	```
   256	
   257	### Error Functions
   258	```bash
   259	# Error reporting functions
   260	error() {
   261	    echo "[ERROR] $*" >&2
   262	}
   263	
   264	warning() {
   265	    echo "[WARNING] $*" >&2
   266	}
   267	
   268	die() {
   269	    error "$*"
   270	    exit 1
   271	}
   272	
   273	# Usage
   274	[[ -f "${FILE}" ]] || die "File ${FILE} not found"
   275	
   276	if [[ ${count} -lt 1 ]]; then
   277	    warning "Count is less than 1, using default"
   278	    count=1
   279	fi
   280	```
   281	
   282	## Performance Considerations
   283	
   284	### Avoid Unnecessary Subprocess Creation
   285	```bash
   286	# BAD: Creates subprocess
   287	output=$(cat file.txt)
   288	
   289	# GOOD: Use built-in
   290	output=$(< file.txt)
   291	
   292	# BAD: External command
   293	basename=$(basename "${filepath}")
   294	
   295	# GOOD: Parameter expansion
   296	basename="${filepath##*/}"
   297	
   298	# BAD: External dirname
   299	dir=$(dirname "${filepath}")
   300	
   301	# GOOD: Parameter expansion
   302	dir="${filepath%/*}"
   303	```
   304	
   305	### Use Built-in Commands
   306	```bash
   307	# String manipulation
   308	filename="document.txt"
   309	
   310	# Extension
   311	ext="${filename##*.}"        # txt
   312	
   313	# Basename without extension
   314	base="${filename%.*}"        # document
   315	
   316	# Remove prefix
   317	path="/usr/local/bin/script.sh"
   318	script="${path##*/}"         # script.sh
   319	
   320	# Remove suffix
   321	dir="${path%/*}"             # /usr/local/bin
   322	```
   323	
   324	### Array Usage
   325	```bash
   326	# Use arrays instead of string splitting
   327	# BAD:
   328	files="file1.txt file2.txt file3.txt"
   329	for file in ${files}; do
   330	    process "${file}"
   331	done
   332	
   333	# GOOD:
   334	files=("file1.txt" "file2.txt" "file3.txt")
   335	for file in "${files[@]}"; do
   336	    process "${file}"
   337	done
   338	
   339	# Read lines into array
   340	mapfile -t lines < file.txt
   341	# Or for older bash:
   342	while IFS= read -r line; do
   343	    lines+=("${line}")
   344	done < file.txt
   345	```
   346	
   347	### Avoid Useless Use of Cat (UUOC)
   348	```bash
   349	# BAD:
   350	cat file.txt | grep pattern
   351	
   352	# GOOD:
   353	grep pattern file.txt
   354	
   355	# BAD:
   356	cat file.txt | while read line; do
   357	    process "${line}"
   358	done
   359	
   360	# GOOD:
   361	while read -r line; do
   362	    process "${line}"
   363	done < file.txt
   364	```
   365	
   366	### Parallel Processing
   367	```bash
   368	# Run commands in parallel
   369	process_file() {
   370	    local file="$1"
   371	    # Process file
   372	    echo "Processing ${file}"
   373	    sleep 1
   374	}
   375	
   376	export -f process_file
   377	
   378	# Using GNU parallel
   379	find . -name "*.txt" | parallel process_file
   380	
   381	# Using xargs
   382	find . -name "*.txt" | xargs -P 4 -I {} bash -c 'process_file "$@"' _ {}
   383	
   384	# Using background jobs
   385	for file in *.txt; do
   386	    process_file "${file}" &
   387	done
   388	wait
   389	```
   390	
   391	## Security Best Practices
   392	
   393	### Input Validation
   394	```bash
   395	# Validate input
   396	validate_integer() {
   397	    local value="$1"
   398	    [[ "${value}" =~ ^[0-9]+$ ]]
   399	}
   400	
   401	validate_email() {
   402	    local email="$1"
   403	    [[ "${email}" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]
   404	}
   405	
   406	# Use it
   407	read -rp "Enter a number: " num
   408	if ! validate_integer "${num}"; then
   409	    die "Invalid number: ${num}"
   410	fi
   411	```
   412	
   413	### Quote Variables
   414	```bash
   415	# ALWAYS quote variables to prevent word splitting and globbing
   416	# BAD:
   417	file=$1
   418	cat $file
   419	
   420	# GOOD:
   421	file="$1"
   422	cat "${file}"
   423	
   424	# Arrays
   425	files=("file 1.txt" "file 2.txt")
   426	# BAD:
   427	for file in ${files[@]}; do
   428	    echo $file
   429	done
   430	
   431	# GOOD:
   432	for file in "${files[@]}"; do
   433	    echo "${file}"
   434	done
   435	```
   436	
   437	### Avoid eval
   438	```bash
   439	# BAD: Security risk
   440	user_input="$1"
   441	eval "${user_input}"
   442	
   443	# GOOD: Use indirect expansion or arrays
   444	# For variable indirection:
   445	var_name="my_var"
   446	my_var="value"
   447	value="${!var_name}"
   448	
   449	# For commands, use array:
   450	cmd=(docker run -it ubuntu)
   451	"${cmd[@]}"
   452	```
   453	
   454	### Secure Temporary Files
   455	```bash
   456	# Use mktemp for temporary files
   457	TEMP_FILE="$(mktemp)" || die "Failed to create temp file"
   458	trap 'rm -f "${TEMP_FILE}"' EXIT
   459	
   460	# Secure permissions
   461	TEMP_DIR="$(mktemp -d)" || die "Failed to create temp directory"
   462	chmod 700 "${TEMP_DIR}"
   463	trap 'rm -rf "${TEMP_DIR}"' EXIT
   464	```
   465	
   466	### Sanitize Paths
   467	```bash
   468	# Prevent directory traversal
   469	sanitize_path() {
   470	    local path="$1"
   471	    local base_dir="$2"
   472	    
   473	    # Resolve to absolute path
   474	    local abs_path
   475	    abs_path="$(cd "$(dirname "${path}")" && pwd)/$(basename "${path}")"
   476	    
   477	    # Check if path is under base_dir
   478	    case "${abs_path}" in
   479	        "${base_dir}"*)
   480	            echo "${abs_path}"
   481	            return 0
   482	            ;;
   483	        *)
   484	            echo "Error: Path outside base directory" >&2
   485	            return 1
   486	            ;;
   487	    esac
   488	}
   489	```
   490	
   491	### Environment Variables
   492	```bash
   493	# Don't expose sensitive data in process list
   494	# BAD:
   495	mysql -u root -pSECRET_PASSWORD
   496	
   497	# GOOD: Use config files or prompt
   498	mysql --defaults-file=/path/to/config
   499	
   500	# Or read from secure source
   501	read -rs -p "Enter password: " password
   502	echo
   503	mysql -u root -p"${password}"
   504	
   505	# Use environment files
   506	if [[ -f .env ]]; then
   507	    set -a
   508	    source .env
   509	    set +a
   510	fi
   511	```
   512	
   513	## Testing Approaches
   514	
   515	### Unit Testing with BATS
   516	```bash
   517	#!/usr/bin/env bats
   518	
   519	# tests/test_common.sh
   520	
   521	setup() {
   522	    # Run before each test
   523	    source ../lib/common.sh
   524	    TEMP_DIR="$(mktemp -d)"
   525	}
   526	
   527	teardown() {
   528	    # Run after each test
   529	    rm -rf "${TEMP_DIR}"
   530	}
   531	
   532	@test "validate_email returns true for valid email" {
   533	    run validate_email "user@example.com"
   534	    [ "$status" -eq 0 ]
   535	}
   536	
   537	@test "validate_email returns false for invalid email" {
   538	    run validate_email "invalid"
   539	    [ "$status" -ne 0 ]
   540	}
   541	
   542	@test "get_file_size returns correct size" {
   543	    echo "test content" > "${TEMP_DIR}/test.txt"
   544	    run get_file_size "${TEMP_DIR}/test.txt"
   545	    [ "$status" -eq 0 ]
   546	    [ "$output" -gt 0 ]
   547	}
   548	```
   549	
   550	### Manual Testing
   551	```bash
   552	# Add test mode to scripts
   553	TEST_MODE="${TEST_MODE:-false}"
   554	
   555	# Mock external commands in test mode
   556	if [[ "${TEST_MODE}" == "true" ]]; then
   557	    aws() {
   558	        echo "Mock AWS output"
   559	    }
   560	    export -f aws
   561	fi
   562	
   563	# Run script in test mode
   564	TEST_MODE=true ./script.sh
   565	```
   566	
   567	### Debugging
   568	```bash
   569	# Enable debug mode
   570	set -x  # Print commands before executing
   571	
   572	# Or run with debug flag
   573	bash -x script.sh
   574	
   575	# Debug specific sections
   576	set -x
   577	# Debug this section
   578	set +x
   579	
   580	# Use PS4 for better debug output
   581	export PS4='+(${BASH_SOURCE}:${LINENO}): ${FUNCNAME[0]:+${FUNCNAME[0]}(): }'
   582	set -x
   583	```
   584	
   585	### Assertions
   586	```bash
   587	# Assert functions
   588	assert_equals() {
   589	    local expected="$1"
   590	    local actual="$2"
   591	    local message="${3:-}"
   592	    
   593	    if [[ "${expected}" != "${actual}" ]]; then
   594	        echo "Assertion failed: ${message}" >&2
   595	        echo "  Expected: ${expected}" >&2
   596	        echo "  Actual:   ${actual}" >&2
   597	        return 1
   598	    fi
   599	}
   600	
   601	assert_file_exists() {
   602	    local file="$1"
   603	    if [[ ! -f "${file}" ]]; then
   604	        echo "Assertion failed: File ${file} does not exist" >&2
   605	        return 1
   606	    fi
   607	}
   608	
   609	# Usage
   610	result=$(get_value)
   611	assert_equals "expected" "${result}" "get_value should return 'expected'"
   612	assert_file_exists "/path/to/file.txt"
   613	```
   614	
   615	## Documentation Standards
   616	
   617	### Script Header
   618	```bash
   619	#!/usr/bin/env bash
   620	#
   621	# Script Name: backup_database.sh
   622	# Description: Backs up PostgreSQL database to S3 with compression
   623	#              and encryption
   624	# Author: John Doe <john@example.com>
   625	# Created: 2024-01-01
   626	# Modified: 2024-01-15
   627	# Version: 1.2.0
   628	#
   629	# Usage:
   630	#   ./backup_database.sh [options] database_name
   631	#
   632	# Options:
   633	#   -h, --help        Show this help message
   634	#   -v, --verbose     Enable verbose output
   635	#   -c, --compress    Compress backup (default: true)
   636	#   -e, --encrypt     Encrypt backup (default: true)
   637	#
   638	# Examples:
   639	#   ./backup_database.sh mydb
   640	#   ./backup_database.sh --verbose --no-compress mydb
   641	#
   642	# Dependencies:
   643	#   - postgresql-client >= 12
   644	#   - aws-cli >= 2.0
   645	#   - openssl
   646	#
   647	# Environment Variables:
   648	#   AWS_ACCESS_KEY_ID     AWS access key
   649	#   AWS_SECRET_ACCESS_KEY AWS secret key
   650	#   BACKUP_ENCRYPTION_KEY Encryption key for backups
   651	#
   652	# Exit Codes:
   653	#   0 - Success
   654	#   1 - General error
   655	#   2 - Invalid arguments
   656	#   3 - Backup failed
   657	#
   658	```
   659	
   660	### Function Documentation
   661	```bash
   662	#######################################
   663	# Backs up a PostgreSQL database
   664	# Globals:
   665	#   BACKUP_DIR
   666	#   AWS_BUCKET
   667	# Arguments:
   668	#   $1 - Database name
   669	#   $2 - (Optional) Backup filename
   670	# Returns:
   671	#   0 on success, 1 on failure
   672	# Outputs:
   673	#   Writes backup file path to stdout
   674	#   Writes errors to stderr
   675	#######################################
   676	backup_database() {
   677	    local db_name="$1"
   678	    local backup_file="${2:-$(date +%Y%m%d_%H%M%S)_${db_name}.sql}"
   679	    
   680	    # Implementation
   681	}
   682	
   683	#######################################
   684	# Validates email address format
   685	# Arguments:
   686	#   $1 - Email address to validate
   687	# Returns:
   688	#   0 if valid, 1 if invalid
   689	#######################################
   690	validate_email() {
   691	    local email="$1"
   692	    [[ "${email}" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]
   693	}
   694	```
   695	
   696	### Usage Function
   697	```bash
   698	usage() {
   699	    cat << EOF
   700	Usage: $(basename "$0") [OPTIONS] database_name
   701	
   702	Backs up PostgreSQL database to S3 with compression and encryption.
   703	
   704	OPTIONS:
   705	    -h, --help              Show this help message
   706	    -v, --verbose           Enable verbose output
   707	    -c, --compress          Compress backup (default: true)
   708	    -e, --encrypt           Encrypt backup (default: true)
   709	    -o, --output FILE       Output file name
   710	    -b, --bucket BUCKET     S3 bucket name
   711	
   712	EXAMPLES:
   713	    $(basename "$0") mydb
   714	    $(basename "$0") --verbose --output backup.sql mydb
   715	    $(basename "$0") -c -e -b my-bucket mydb
   716	
   717	EXIT CODES:
   718	    0   Success
   719	    1   General error
   720	    2   Invalid arguments
   721	    3   Backup failed
   722	
   723	ENVIRONMENT:
   724	    AWS_ACCESS_KEY_ID       AWS access key
   725	    AWS_SECRET_ACCESS_KEY   AWS secret key
   726	    BACKUP_ENCRYPTION_KEY   Encryption key
   727	
   728	For more information, see: https://example.com/docs
   729	EOF
   730	}
   731	```
   732	
   733	## Common Pitfalls to Avoid
   734	
   735	### 1. Unquoted Variables
   736	```bash
   737	# BAD:
   738	file=$1
   739	if [ -f $file ]; then
   740	    cat $file
   741	fi
   742	
   743	# GOOD:
   744	file="$1"
   745	if [[ -f "${file}" ]]; then
   746	    cat "${file}"
   747	fi
   748	```
   749	
   750	### 2. Using [ Instead of [[
   751	```bash
   752	# BAD: [ is less safe
   753	if [ $var == "test" ]; then
   754	    echo "test"
   755	fi
   756	
   757	# GOOD: [[ is safer and more powerful
   758	if [[ "${var}" == "test" ]]; then
   759	    echo "test"
   760	fi
   761	
   762	# [[ supports pattern matching
   763	if [[ "${file}" == *.txt ]]; then
   764	    echo "Text file"
   765	fi
   766	```
   767	
   768	### 3. Not Checking Command Success
   769	```bash
   770	# BAD:
   771	cd /some/directory
   772	rm -rf *
   773	
   774	# GOOD:
   775	cd /some/directory || die "Failed to change directory"
   776	rm -rf ./*
   777	
   778	# Or:
   779	if ! cd /some/directory; then
   780	    die "Failed to change directory"
   781	fi
   782	```
   783	
   784	### 4. Using ls for Iteration
   785	```bash
   786	# BAD:
   787	for file in $(ls *.txt); do
   788	    process "${file}"
   789	done
   790	
   791	# GOOD:
   792	for file in *.txt; do
   793	    [[ -e "${file}" ]] || continue
   794	    process "${file}"
   795	done
   796	
   797	# Or with globbing disabled check:
   798	shopt -s nullglob
   799	for file in *.txt; do
   800	    process "${file}"
   801	done
   802	```
   803	
   804	### 5. Ignoring Shellcheck
   805	```bash
   806	# Always run shellcheck on your scripts
   807	shellcheck script.sh
   808	
   809	# Address warnings and errors
   810	# Disable specific checks only when necessary
   811	# shellcheck disable=SC2034
   812	UNUSED_VAR="value"  # Used in sourced file
   813	```
   814	
   815	## Language-Specific Idioms and Patterns
   816	
   817	### Parameter Expansion
   818	```bash
   819	# Default values
   820	output="${1:-default.txt}"              # Use $1 or "default.txt"
   821	output="${1:=default.txt}"              # Set $1 to "default.txt" if unset
   822	
   823	# String manipulation
   824	filename="document.txt"
   825	echo "${filename%.txt}"                 # document (remove suffix)
   826	echo "${filename%.*}"                   # document (remove extension)
   827	echo "${filename##*.}"                  # txt (get extension)
   828	
   829	path="/usr/local/bin/script.sh"
   830	echo "${path##*/}"                      # script.sh (basename)
   831	echo "${path%/*}"                       # /usr/local/bin (dirname)
   832	
   833	# String replacement
   834	text="hello world hello"
   835	echo "${text/hello/hi}"                 # hi world hello (first)
   836	echo "${text//hello/hi}"                # hi world hi (all)
   837	
   838	# Case modification (Bash 4+)
   839	echo "${text^^}"                        # HELLO WORLD HELLO (uppercase)
   840	echo "${text,,}"                        # hello world hello (lowercase)
   841	echo "${text^}"                         # Hello world hello (capitalize first)
   842	
   843	# Length
   844	echo "${#text}"                         # 17
   845	
   846	# Substring
   847	echo "${text:0:5}"                      # hello
   848	echo "${text:6}"                        # world hello
   849	```
   850	
   851	### Arrays
   852	```bash
   853	# Declare array
   854	arr=(one two three)
   855	declare -a indexed_array
   856	declare -A assoc_array
   857	
   858	# Access elements
   859	echo "${arr[0]}"                        # one
   860	echo "${arr[@]}"                        # all elements
   861	echo "${arr[*]}"                        # all elements as single word
   862	echo "${#arr[@]}"                       # array length
   863	
   864	# Iterate
   865	for item in "${arr[@]}"; do
   866	    echo "${item}"
   867	done
   868	
   869	# Associative arrays (Bash 4+)
   870	declare -A user
   871	user[name]="John"
   872	user[age]="30"
   873	
   874	# Iterate associative array
   875	for key in "${!user[@]}"; do
   876	    echo "${key}: ${user[${key}]}"
   877	done
   878	
   879	# Append to array
   880	arr+=("four")
   881	
   882	# Array slicing
   883	echo "${arr[@]:1:2}"                    # two three
   884	```
   885	
   886	### Conditionals
   887	```bash
   888	# File tests
   889	[[ -e file ]]       # exists
   890	[[ -f file ]]       # is regular file
   891	[[ -d dir ]]        # is directory
   892	[[ -L link ]]       # is symbolic link
   893	[[ -r file ]]       # is readable
   894	[[ -w file ]]       # is writable
   895	[[ -x file ]]       # is executable
   896	[[ -s file ]]       # has size > 0
   897	
   898	# String tests
   899	[[ -z "$str" ]]     # string is empty
   900	[[ -n "$str" ]]     # string is not empty
   901	[[ "$a" == "$b" ]]  # strings are equal
   902	[[ "$a" != "$b" ]]  # strings are not equal
   903	[[ "$a" < "$b" ]]   # lexicographic comparison
   904	
   905	# Numeric tests
   906	[[ $a -eq $b ]]     # equal
   907	[[ $a -ne $b ]]     # not equal
   908	[[ $a -lt $b ]]     # less than
   909	[[ $a -le $b ]]     # less than or equal
   910	[[ $a -gt $b ]]     # greater than
   911	[[ $a -ge $b ]]     # greater than or equal
   912	
   913	# Logical operators
   914	[[ condition1 && condition2 ]]
   915	[[ condition1 || condition2 ]]
   916	[[ ! condition ]]
   917	
   918	# Pattern matching
   919	[[ "$file" == *.txt ]]
   920	[[ "$string" =~ ^[0-9]+$ ]]  # regex
   921	```
   922	
   923	### Here Documents
   924	```bash
   925	# Basic here document
   926	cat << EOF
   927	This is a multi-line
   928	text with ${variable}
   929	expansion
   930	EOF
   931	
   932	# Prevent expansion
   933	cat << 'EOF'
   934	This has no ${variable}
   935	expansion
   936	EOF
   937	
   938	# Here strings
   939	grep "pattern" <<< "${content}"
   940	
   941	# Indented here document (<<-)
   942	if true; then
   943	    cat <<- EOF
   944	                This is indented
   945	                in the script
   946	        EOF
   947	fi
   948	```
   949	
   950	### Process Substitution
   951	```bash
   952	# Compare output of two commands
   953	diff <(ls dir1) <(ls dir2)
   954	
   955	# Read from command output
   956	while read -r line; do
   957	    process "${line}"
   958	done < <(find . -name "*.txt")
   959	
   960	# Multiple inputs
   961	paste <(cut -f1 file1) <(cut -f1 file2)
   962	```
   963	
   964	### Command Substitution
   965	```bash
   966	# Modern syntax (preferred)
   967	output=$(command)
   968	files=($(ls *.txt))
   969	
   970	# Use quotes to preserve whitespace
   971	content="$(cat file.txt)"
   972	
   973	# Capture both stdout and stderr
   974	output=$(command 2>&1)
   975	```
   976	
   977	### Functions
   978	```bash
   979	# Basic function
   980	greet() {
   981	    echo "Hello, $1!"
   982	}
   983	
   984	# Local variables
   985	calculate() {
   986	    local a="$1"
   987	    local b="$2"
   988	    local result=$((a + b))
   989	    echo "${result}"
   990	}
   991	
   992	# Return values (use echo and capture)
   993	get_value() {
   994	    echo "returned value"
   995	}
   996	value=$(get_value)
   997	
   998	# Return codes
   999	is_valid() {
  1000	    [[ "$1" =~ ^[0-9]+$ ]]
  1001	    return $?  # Return last command's exit code
  1002	}
  1003	
  1004	if is_valid "123"; then
  1005	    echo "Valid"
  1006	fi
  1007	```
  1008	
  1009	### Arithmetic
  1010	```bash
  1011	# Arithmetic expansion
  1012	result=$((5 + 3))
  1013	result=$((a * b))
  1014	result=$((count++))
  1015	result=$((count--))
  1016	
  1017	# Arithmetic evaluation
  1018	((count++))
  1019	((total += value))
  1020	
  1021	if ((count > 10)); then
  1022	    echo "Count is greater than 10"
  1023	fi
  1024	
  1025	# Use bc for floating point
  1026	result=$(echo "scale=2; 10 / 3" | bc)
  1027	```
  1028	
  1029	### Loops
  1030	```bash
  1031	# For loop
  1032	for i in {1..10}; do
  1033	    echo "${i}"
  1034	done
  1035	
  1036	# For loop with step
  1037	for i in {0..100..10}; do
  1038	    echo "${i}"
  1039	done
  1040	
  1041	# C-style for loop
  1042	for ((i=0; i<10; i++)); do
  1043	    echo "${i}"
  1044	done
  1045	
  1046	# While loop
  1047	while read -r line; do
  1048	    process "${line}"
  1049	done < file.txt
  1050	
  1051	# Until loop
  1052	counter=0
  1053	until ((counter >= 10)); do
  1054	    echo "${counter}"
  1055	    ((counter++))
  1056	done
  1057	
  1058	# Infinite loop
  1059	while true; do
  1060	    do_something
  1061	    sleep 1
  1062	done
  1063	```
  1064	
  1065	### POSIX Compliance
  1066	```bash
  1067	#!/bin/sh
  1068	# For maximum portability, use POSIX sh
  1069	
  1070	# Use [ instead of [[
  1071	if [ "$var" = "test" ]; then
  1072	    echo "test"
  1073	fi
  1074	
  1075	# Use case for pattern matching
  1076	case "$file" in
  1077	    *.txt) echo "Text file" ;;
  1078	    *.sh)  echo "Shell script" ;;
  1079	    *)     echo "Unknown" ;;
  1080	esac
  1081	
  1082	# Don't use bash-specific features
  1083	# - No [[ ]]
  1084	# - No (( ))
  1085	# - No ${var^^}
  1086	# - No process substitution
  1087	# - No arrays (use positional parameters)
  1088	```
  1089	


---

## Shell Compatibility Guide (Bash/Zsh/Sh)

### Shell Type Detection

Always specify the shell type explicitly in your shebang:

```bash
#!/usr/bin/env bash   # Use env for portability (searches PATH)
#!/bin/bash           # Direct path (faster, less portable)
#!/usr/bin/env zsh    # For zsh scripts
#!/bin/sh             # For POSIX sh scripts (maximum compatibility)
#!/bin/dash           # For dash (faster POSIX sh)
#!/bin/ksh            # For KornShell
```

### Shell-Specific Features Comparison

#### Bash Features (Not in POSIX sh)
```bash
# Arrays
declare -a array=("item1" "item2" "item3")
echo "${array[0]}"

# Associative arrays (Bash 4.0+)
declare -A assoc_array
assoc_array[key]="value"

# [[ ]] conditional tests (advanced)
if [[ "$var" =~ ^[0-9]+$ ]]; then
    echo "Numeric"
fi

# Process substitution
diff <(sort file1) <(sort file2)

# String manipulation
echo "${var^^}"  # Uppercase
echo "${var,,}"  # Lowercase

# Arithmetic
((result = 5 + 3))
echo "$((5 + 3))"

# Here-strings
cat <<< "string"
```

#### Zsh Features
```bash
# Arrays (1-indexed, not 0-indexed!)
array=(item1 item2 item3)
echo "$array[1]"  # First element (not array[0])

# Glob qualifiers
ls *(.)   # Only regular files
ls *(/)   # Only directories
ls *(.mm-7)  # Files modified in last 7 days

# Advanced parameter expansion
echo ${(U)var}  # Uppercase
echo ${(L)var}  # Lowercase
echo ${(C)var}  # Capitalize

# Array slicing
echo $array[1,3]  # Elements 1 to 3

# Setopt for behavior control
setopt EXTENDED_GLOB
setopt NULL_GLOB
```

#### POSIX sh Compatibility (Works Everywhere)
```bash
#!/bin/sh

# Use [ ] for tests, NOT [[ ]]
if [ "$var" = "value" ]; then
    echo "Match"
fi

# Use case for pattern matching
case "$var" in
    pattern) echo "matched" ;;
esac

# Use command substitution
result=$(command)

# Use arithmetic with expr (portable but slow)
result=$(expr 5 + 3)

# Or use $(( )) for arithmetic (POSIX but limited)
result=$((5 + 3))

# NO arrays - use positional parameters or delimited strings
set -- item1 item2 item3
echo "$1"  # First item

# Use printf instead of echo for portability
printf '%s\n' "text"

# Function syntax (POSIX)
function_name() {
    # No local keyword in pure POSIX sh
    # Use _ prefix for "local" variables
    _local_var="value"
}
```

### Cross-Shell Compatibility Patterns

#### Variable Quoting (All Shells)
```bash
# ALWAYS quote variables
echo "$var"
echo "${var}"

# Quote in conditions
if [ "$var" = "value" ]; then
    # ...
fi

# Quote in assignments with spaces
path="/path/to/my dir"  # Still quote usage: "$path"
```

#### Function Definitions (Portable)
```bash
# POSIX-compatible function syntax
function_name() {
    # Function body
    return 0
}

# Bash/Zsh also support 'function' keyword
function function_name {
    # Function body
}

# For maximum portability, use () syntax
```

#### Conditional Tests

##### POSIX-Compatible Tests
```bash
# String comparison
[ "$a" = "$b" ]      # Equal
[ "$a" != "$b" ]     # Not equal
[ -z "$a" ]          # Empty string
[ -n "$a" ]          # Non-empty string

# Numeric comparison
[ "$a" -eq "$b" ]    # Equal
[ "$a" -ne "$b" ]    # Not equal
[ "$a" -lt "$b" ]    # Less than
[ "$a" -le "$b" ]    # Less than or equal
[ "$a" -gt "$b" ]    # Greater than
[ "$a" -ge "$b" ]    # Greater than or equal

# File tests
[ -f "$file" ]       # Is regular file
[ -d "$dir" ]        # Is directory
[ -e "$path" ]       # Exists
[ -r "$file" ]       # Is readable
[ -w "$file" ]       # Is writable
[ -x "$file" ]       # Is executable

# Logical operators
[ "$a" = "x" ] && [ "$b" = "y" ]  # AND
[ "$a" = "x" ] || [ "$b" = "y" ]  # OR
[ ! -f "$file" ]                   # NOT
```

##### Bash/Zsh Advanced Tests
```bash
# [[ ]] provides more features (NOT POSIX)
[[ "$var" =~ ^[0-9]+$ ]]  # Regex matching
[[ "$var" == pat* ]]       # Pattern matching
[[ "$a" < "$b" ]]          # String comparison (lexicographic)
[[ -z "$var" ]]            # Empty (same as [ ])
```

### Shell Detection in Scripts

```bash
#!/bin/sh
# Detect which shell is running this script

detect_shell() {
    if [ -n "$BASH_VERSION" ]; then
        echo "bash"
    elif [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$KSH_VERSION" ]; then
        echo "ksh"
    else
        # Likely POSIX sh or dash
        echo "sh"
    fi
}

shell_type=$(detect_shell)
echo "Running under: $shell_type"

# Conditional behavior based on shell
case "$shell_type" in
    bash)
        # Use bash-specific features
        ;;
    zsh)
        # Use zsh-specific features
        ;;
    *)
        # Use only POSIX features
        ;;
esac
```

### Common Portability Pitfalls

#### Echo vs Printf
```bash
# DON'T: echo behavior varies
echo -n "text"      # May not work in all shells
echo -e "tab:\t"    # May not work in all shells

# DO: Use printf for portability
printf '%s' "text"
printf 'tab:\t\n'
```

#### Local Variables
```bash
# Bash/Zsh: local keyword works
function_name() {
    local var="value"
}

# POSIX sh: NO local keyword
function_name() {
    # Use underscore prefix convention
    _var="value"
    # Or use positional parameters
}
```

#### Arrays
```bash
# Bash: Arrays available
declare -a array=(1 2 3)
echo "${array[0]}"

# POSIX sh: NO arrays, use alternatives
# Option 1: Positional parameters
set -- 1 2 3
echo "$1"

# Option 2: Delimited strings
items="1:2:3"
# Parse with IFS or cut/awk

# Option 3: Multiple variables
item1=1
item2=2
item3=3
```

#### String Manipulation
```bash
# Bash: Built-in string operations
echo "${var^^}"        # Uppercase (Bash 4.0+)
echo "${var:0:5}"      # Substring

# POSIX sh: Use external tools
echo "$var" | tr '[:lower:]' '[:upper:]'  # Uppercase
echo "$var" | cut -c1-5                    # Substring
```

### Writing Portable Scripts

#### Best Practices for Portability

1. **Use POSIX sh when possible**
   - Widest compatibility
   - Faster (especially with dash)
   - Easier to maintain

2. **Explicitly state shell requirements**
   ```bash
   #!/bin/bash
   # Requires: bash 4.0+
   # Reason: Uses associative arrays
   ```

3. **Test on multiple shells**
   ```bash
   # Test script on different shells
   bash script.sh
   dash script.sh
   zsh script.sh
   ```

4. **Use ShellCheck**
   ```bash
   # Install shellcheck
   shellcheck script.sh
   
   # Specify shell
   shellcheck --shell=bash script.sh
   shellcheck --shell=sh script.sh
   ```

5. **Document non-portable features**
   ```bash
   # This script uses bash-specific features:
   # - Associative arrays (Bash 4.0+)
   # - Process substitution
   # - [[ ]] tests
   ```

### Shell-Specific Optimizations

#### Bash Optimizations
```bash
# Use built-in commands instead of external
# BAD: Slow, spawns process
result=$(echo "$var" | grep pattern)

# GOOD: Fast, uses bash built-ins
[[ "$var" =~ pattern ]]

# Use parameter expansion instead of sed/awk
# BAD:
result=$(echo "$var" | sed 's/old/new/')

# GOOD:
result="${var/old/new}"
```

#### POSIX sh Optimizations
```bash
# Minimize external command calls
# BAD: Multiple calls
count=$(echo "$str" | wc -c)
count=$(expr $count - 1)

# BETTER: Single call
count=$(printf '%s' "$str" | wc -c)

# Use built-in : instead of true
while :; do  # Faster than while true
    # ...
done
```

### Migration Guide

#### Converting Bash Scripts to POSIX sh

```bash
# Bash script:
#!/bin/bash
declare -a files=(file1.txt file2.txt)
for file in "${files[@]}"; do
    [[ -f "$file" ]] && echo "Found: $file"
done

# POSIX sh equivalent:
#!/bin/sh
set -- file1.txt file2.txt
for file in "$@"; do
    [ -f "$file" ] && echo "Found: $file"
done
```

#### Converting POSIX sh to Bash (for features)

```bash
# POSIX sh (limited):
#!/bin/sh
IFS=:
set -- $PATH
for dir in "$@"; do
    echo "$dir"
done

# Bash (cleaner with arrays):
#!/bin/bash
IFS=: read -ra paths <<< "$PATH"
for dir in "${paths[@]}"; do
    echo "$dir"
done
```

---

## Shell Compatibility Checklist

When writing shell scripts, consider:

- [ ] Shebang specifies correct shell type
- [ ] Uses only features available in target shell
- [ ] Variables are properly quoted
- [ ] Tests use correct syntax ([ ] for POSIX, [[ ]] for Bash/Zsh)
- [ ] No bashisms if targeting POSIX sh
- [ ] Functions use portable syntax
- [ ] Error handling is appropriate for shell type
- [ ] Script tested on target shell(s)
- [ ] ShellCheck passes with correct shell specified
- [ ] Documentation states shell requirements

---

**Last Updated:** October 12, 2025
**Shell Compatibility:** Bash 4.0+, Zsh 5.0+, POSIX sh, Dash, KornShell
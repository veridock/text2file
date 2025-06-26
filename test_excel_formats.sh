#!/bin/bash

# Create output directory if it doesn't exist
mkdir -p test_output

# Test 1: Basic XLSX with simple data
echo -e "\n=== Test 1: Basic XLSX ==="
cat > test_output/basic_data.csv << 'EOL'
Name,Age,City
John,30,New York
Alice,25,London
EOL
cat test_output/basic_data.csv | text2file generate - xlsx -o test_output -p basic_data

# Test 2: XLS format
echo -e "\n=== Test 2: XLS Format ==="
cat > test_output/products.csv << 'EOL'
Product,Price,Stock
Laptop,999.99,15
Mouse,25.5,100
EOL
cat test_output/products.csv | text2file generate - xls -o test_output -p products

# Test 3: XLSX with dates and numbers
echo -e "\n=== Test 3: XLSX with Dates/Numbers ==="
cat > test_output/finances.csv << 'EOL'
Date,Amount,Description
2025-01-15,1250.75,Salary
2025-01-20,-350.25,Rent
EOL
cat test_output/finances.csv | text2file generate - xlsx -o test_output -p finances

# Test 4: XLSX with simple data (formulas not supported in CSV input)
echo -e "\n=== Test 4: XLSX with Simple Data ==="
cat > test_output/simple_data.csv << 'EOL'
A,B,C,Sum
1,10,20,30
2,20,30,50
EOL
cat test_output/simple_data.csv | text2file generate - xlsx -o test_output -p simple_data

# Test 5: Medium dataset (20 rows)
echo -e "\n=== Test 5: Medium Dataset (20 rows) ==="
cat > test_output/medium_data.csv << 'EOL'
ID,Name,Value
EOL
for i in {1..20}; do
    echo "$i,Item$i,$((RANDOM%1000)).$((RANDOM%100))" >> test_output/medium_data.csv
done
cat test_output/medium_data.csv | text2file generate - xlsx -o test_output -p medium_data

echo -e "\n=== Test Complete ==="
ls -lh test_output/*.{xls,xlsx} 2>/dev/null || echo "No Excel files found in test_output/"

echo -e "\n=== Verifying Excel Files ==="
for file in test_output/*.{xls,xlsx} 2>/dev/null; do
    if [ -f "$file" ]; then
        echo -e "\nFile: $file"
        python3 check_excel.py "$file"
    fi
done

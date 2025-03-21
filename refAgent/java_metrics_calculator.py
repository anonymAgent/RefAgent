import javalang
import os
import glob
import subprocess
import pandas as pd
from collections import defaultdict

class JavaMetricsCalculator:
    def __init__(self, input_path, output_path, designite_jar):
        """
        Initialize the calculator with paths for input code, output metrics, and DesigniteJava.jar.
        :param input_path: Path to the folder containing Java code.
        :param output_path: Path to store DesigniteJava outputs.
        :param designite_jar: Path to the DesigniteJava jar file.
        """
        self.metrics = defaultdict(dict)
        self.input_path = input_path
        self.output_path = output_path
        self.designite_jar = designite_jar
        self.method_metrics_file = os.path.join(output_path, 'methodMetrics.csv')
        self.type_metrics_file = os.path.join(output_path, 'typeMetrics.csv')
        self.java_code = None

    def parse_java_code(self, file_path):
        with open(file_path, 'r') as f:
            self.java_code = f.read()
            
    def run_designite(self):
        """
        Run the DesigniteJava tool to generate method and type metrics.
        """
        command = [
            "java", "-jar", self.designite_jar,
            "-i", self.input_path,
            "-o", self.output_path
        ]
        try:
            print("Executing DesigniteJava tool...")
            subprocess.run(command, check=True)
            print("DesigniteJava execution completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error executing DesigniteJava: {e}")

    def parse_metrics(self):
        """
        Parse the generated CSV files for method and class-level metrics.
        """
        if not (os.path.exists(self.method_metrics_file) and os.path.exists(self.type_metrics_file)):
            print("Metrics files not found. Ensure DesigniteJava execution is successful.")
            return

        # Read method metrics
        method_metrics = pd.read_csv(self.method_metrics_file)
        type_metrics = pd.read_csv(self.type_metrics_file)

        # Process method metrics for each class
        for _, row in method_metrics.iterrows():
            class_name = row['Type Name']
            method_name = row['MethodName']
            cc = row['CC']  # Cyclomatic Complexity
            loc = row['LOC']  # Lines of Code
            pc = row['PC']  # Parameter Count

            if class_name not in self.metrics:
                self.metrics[class_name]['methods'] = []

            self.metrics[class_name]['methods'].append({
                "Method Name": method_name,
                "Cyclomatic Complexity (CC)": cc,
                "Lines of Code (LOC)": loc,
                "Parameter Count (PC)": pc
            })

        # Process class/type metrics
        for _, row in type_metrics.iterrows():
            class_name = row['Type Name']
            self.metrics[class_name]['class_metrics'] = {
                "Number of Fields (NOF)": row['NOF'],
                "Number of Public Fields (NOPF)": row['NOPF'],
                "Number of Methods (NOM)": row['NOM'],
                "Number of Public Methods (NOPM)": row['NOPM'],
                "Lines of Code (LOC)": row['LOC'],
                "Weighted Methods per Class (WMC)": row['WMC'],
                "Lack of Cohesion of Methods (LCOM)": row['LCOM']
            }
        print("Metrics parsing completed.")

    def compute_metrics_for_class(self):
        """
        Collect and return metrics for all classes in the project.
        :return: A dictionary containing method-level and class-level metrics.
        """
        # Execute the Designite tool
        self.run_designite()

        # Parse the CSV files
        self.parse_metrics()

        # Prepare the metrics dictionary
        final_metrics = {}
        for class_name, data in self.metrics.items():
            class_metrics = data.get('class_metrics', {})
            method_metrics = data.get('methods', [])
            final_metrics[class_name] = {
                "Class Metrics": class_metrics,
                "Method Metrics": method_metrics
            }
        return final_metrics

    def get_metrics(self):
        """
        Get the computed metrics.
        :return: Dictionary of computed metrics.
        """
        return self.metrics
    
    def as_string(self):
        """
        Return the metrics as a formatted string for display.
        """
        result = []
        for class_name, metric in self.metrics.items():
            result.append(f"Class: {class_name}")
            result.append("Class Metrics:")
            for k, v in metric.get("class_metrics", {}).items():
                result.append(f"  {k}: {v}")
            result.append("Method Metrics:")
            for method in metric.get("methods", []):
                result.append(f"  Method: {method['Method Name']}")
                result.append(f"    Cyclomatic Complexity (CC): {method['Cyclomatic Complexity (CC)']}")
                result.append(f"    Lines of Code (LOC): {method['Lines of Code (LOC)']}")
                result.append(f"    Parameter Count (PC): {method['Parameter Count (PC)']}")
            result.append("\n")
        return "\n".join(result)
    
    def clean_repository(self):
        """
        Clean the input and output paths by removing all .java files and temporary files.
        """
        print("Cleaning repository...")
        # Clean .java files in input_path
        java_files = glob.glob(os.path.join(self.input_path, "**/*.java"), recursive=True)
        for file_path in java_files:
            try:
                os.remove(file_path)
                print(f"Removed Java file: {file_path}")
            except Exception as e:
                print(f"Error removing Java file {file_path}: {e}")
        
        # Clean temporary files in output_path
        extensions_to_remove = ['*.csv', '*.log', '*.tmp']
        for ext in extensions_to_remove:
            for file_path in glob.glob(os.path.join(self.output_path, ext)):
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
        print("Repository cleaning completed.")

# Example Usage
if __name__ == "__main__":
    input_path = "code_smells/project"  # Path to the Java code directory
    output_path = "./code_smells/designite_output"   # Path to store metrics
    designite_jar = "./code_smells/DesigniteJava.jar"  # Path to DesigniteJava.jar

    calculator = JavaMetricsCalculator(input_path, output_path, designite_jar)
    metrics = calculator.compute_metrics_for_class()
    print(calculator.as_string())




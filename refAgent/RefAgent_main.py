from refAgent.java_metrics_calculator import JavaMetricsCalculator
from refAgent.dependency_graph import JavaClassDependencyAnalyzer, draw_dependency_graph
from utilities import *
from refAgent.OpenaiLLM import OpenAILLM
import sys
from settings import Settings
import argparse

# === Parse project name argument ===
parser = argparse.ArgumentParser(description="Refactor Java Project")
parser.add_argument("project_name", type=str, help="Name of the project folder (e.g. accumulo-2.1)")
args = parser.parse_args()

protject_name = args.project_name

config = Settings()
# Example usage
if __name__ == "__main__":

    #Prepare needed folders
    results = {}
    os.makedirs(f"results/{protject_name}", exist_ok=True)
    os.makedirs(f"data/paths/{protject_name}", exist_ok=True)

    #Identify the .java files in  REPO
    export_java_files_to_json(f"projects/before/{protject_name}", f"data/paths/{protject_name}/{protject_name}_files.json")
    files = read_json_file(f"data/paths/{protject_name}/{protject_name}_files.json")
    files = find_non_test_files(files)
    for file in files:
        try:
            project_directory = f"projects/before/{protject_name}"
            target_class = extract_class_name(file)
            class_directory = os.path.dirname(file)

            if target_class == None:
                continue
            os.makedirs(f"results/{protject_name}/{target_class}", exist_ok=True)

            graph_path = f"data/graphs/{protject_name}/{target_class}_dependency_graph.json"
            
            analyzer = JavaClassDependencyAnalyzer(target_class)
            analyzer.analyze_project(project_directory)
            analyzer.export_to_json(graph_path)
            draw_dependency_graph(analyzer.dependencies, filename=f"data/graphs/{protject_name}/{target_class}_dependency_graph.png")
            
            # 1. For a single file
            input_path = "code_smells/project/before"  # Path to the Java code directory
            output_path = "./code_smells/tmp/before"   # Path to store metrics
            designite_jar = "./code_smells/DesigniteJava.jar"  # Path to DesigniteJava.jar

            copy_file(class_directory, input_path, target_class+".java")

            before_calculator = JavaMetricsCalculator(input_path, output_path, designite_jar)
            before_calculator.parse_java_code(file)
            before_metrics = before_calculator.compute_metrics_for_class()
            before_calculator.clean_repository()

            path_to_java_file = file
            path_to_java_file_after = path_to_java_file.replace("before","after")

            Before_java_code = before_calculator.java_code

            #Export the CKO metrics of the original class to results folder
            results["CKO metrics"] = before_metrics

            # Example usage:
            api_key = config.API_KEY
            llm = OpenAILLM(api_key)
            prompt = "You are a software developer, helpull and a java expert"

            query = """
                For each method in the provided Java class : 
                {} 
                
                Return "Yes or No based on wether the method needs refactoring and improvement to enhance is readaoilty and maintainability clarity. and adherence to basic coding practices. . 
                Ensure that your assessment considers the method's complexity, the class weighted Methods per class, the lack of cohesion of methods in the class.
                
                Class CKO metrics : 
                {}

                Provide your response in a json format as follow : 
                {{
                Method1: (yes, improvement instruction),
                Method2: No,
                Method3: (yes, improvement instruction)
                }}

                Avoid using natural lanquage explanation
                """.format(before_calculator.java_code, before_calculator.as_string())
                
            Instruction = llm.query_llm(prompt, query, model=config.MODEL_NAME)
            results["Instruction"] = Instruction

            #Decision Node
            query_decisition = """
                    Output: True or false

                    From this set of instructoin to improve all these methods does as least one method need improvement:

                    Instruction: {}

                    Don't return any natural language explanation
                    """.format(Instruction)
            do_instrect = llm.query_llm(prompt, query_decisition, model=config.MODEL_NAME)
            
            if do_instrect:   

                for i in range(5): 
                    query = """
                            Following the instruction Instructions:{}  and CKO metrics {} and dependent calsses, improve the provided java code {} and improve the
                            CKO metrics. You can assume that the given class and methods are functionally correct. Ensure that you do not
                            Alter the behaviour of the external method while maintaining the behaviour of the method, maintaining both syntactic
                            and semantic corectness. Don't remove any comments or annotations.
                            Provide the java class within code block. Avoid using natural langiage explanations
                            """.format(Instruction, before_metrics,Before_java_code)
                    improvement = llm.query_llm(prompt, query, model=config.MODEL_NAME)
                    improvement = improvement.replace("```java", "").replace("```", "")

                    print(f"------------ Start making the improvement to compile and test Itteration {i}-----------------")
                    print(f"=============================================================================================")

                    write_to_java_file(file_path=path_to_java_file_after, java_code=improvement)

                    #Write the improved code in the results file
                    write_to_java_file(file_path=f"results/{protject_name}/{target_class}/original_java_code.java", java_code=Before_java_code)
                    write_to_java_file(file_path=f"results/{protject_name}/{target_class}/improved_java_code.java", java_code=improvement)


                    print("-------------------- Compile the improved code ---------------------------------------")

                    project_directory = f"projects_after/{protject_name}"
                    is_compiled = compile_project_with_maven(project_directory)
                    if is_compiled == False:
                        results["Compilation"] = False
                        results["Test passed"] = False
                        results["is improved"] = False 
                        write_to_java_file(file_path=path_to_java_file_after, java_code=Before_java_code)
                        continue

                    print("------------ Test the improved code ---------------------------------------")
                    graph_dep = read_json_file(graph_path)
                    files = extract_ids(graph_dep)
                    tests = find_test_files(files)
                    for test in tests:
                        if test!="TestCase":
                            rcode = run_maven_test(test, project_dir=project_directory, verify=False)
                            if rcode.returncode != 0:
                                results["Compilation"] = True
                                results["Test passed"] = False
                                results["is improved"] = False
                                continue  
                    print("------------- Commit the code changes to github-------------------")

                    repo_path = f'projects/after/{protject_name}'
                    file_path = file.replace(f"projects/before/{protject_name}/", "")

                    commit_message = f'Your changing file {file_path}'
                    commit_file_to_github(repo_path, file_path, commit_message)   

                    #Compute CKO metrics
                    # 1. For a single file
                    # 1. For a single file
                    input_path = "code_smells/project/after"  # Path to the Java code directory
                    output_path = "./code_smells/tmp/after"   # Path to store metrics

                    write_to_java_file(file_path=input_path+"/"+target_class+".java", java_code=improvement)


                    after_calculator = JavaMetricsCalculator(input_path, output_path, designite_jar)
                    after_calculator.parse_java_code(file)
                    after_metrics = before_calculator.compute_metrics_for_class()
                    after_calculator.clean_repository()

                    # Check there was an improvement
                    query = """
                            Given the Java code before and after the proposed changes, along with their corresponding CKO metrics, 
                            assess whether the code has improved. Analyze both versions of the code and compare the CKO metrics.
                            Determine if the changes resulted in better code quality, readability, maintainability, and performance.
                            Java code before improvement :{}
                            CKO metrics before improvement : {}
                            
                            Java code after Improvement: {}
                            CKO metrics after Improvement: {}

                            Return True or False.
                            Avoid using natural lanquage explanation
                            """.format(Before_java_code, after_metrics,improvement, after_metrics)
                    
                    is_improvement = llm.query_llm(prompt, query, model=config.MODEL_NAME)
                    if is_improvement ==False:
                        results["Compilation"] = True
                        results["Test passed"] = True
                        results["is improved"] = False
                        continue
                            
                    results["Compilation"] = True
                    results["Test passed"] = True
                    results["is improved"] = True
                    results["CKO metrics After"] = after_metrics

                    break
                
                write_to_java_file(file_path=path_to_java_file_after, java_code=Before_java_code)
                export_dict_to_json(results, f"results/{protject_name}/{target_class}/metrics")
        except:
            continue
            








        

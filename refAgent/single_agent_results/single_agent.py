from utilities import *
from OpenaiLLM import OpenAILLM
import sys
from settings import Settings

config = Settings()
# Example usage
if __name__ == "__main__":

    #Prepare needed folders
    results = {}
    protject_name = "jclouds"
    os.makedirs(f"single_agent_results/{protject_name}", exist_ok=True)
    os.makedirs(f"single_agent_results/data/paths/{protject_name}", exist_ok=True)

    #Identify the .java files in  REPO
    export_java_files_to_json(f"projects/{protject_name}", f"single_agent_results/data/paths/{protject_name}/{protject_name}_files.json")
    files = read_json_file(f"single_agent_results/data/paths/{protject_name}/{protject_name}_files.json")
    files = find_non_test_files(files)
    for file in files:
        results = {}
        results["Compilation"] = True
        results["Test passed"] = True
        results["is improved"] = True
        try:
            project_directory = f"projects/{protject_name}"
            target_class = extract_class_name(file)
            class_directory = os.path.dirname(file)

            if target_class == None:
                continue
            os.makedirs(f"single_agent_results/{protject_name}/{target_class}", exist_ok=True)


            path_to_java_file = file
            path_to_java_file_after = path_to_java_file.replace("projects","projects_after")
            path_to_java_file_after = "single_agent_results/"+path_to_java_file_after

            java_code = parse_java_code(path_to_java_file)


            # Example usage:
            api_key = config.API_KEY
            llm = OpenAILLM(api_key)
            prompt = """ Instruction
                    You are a powerful model specialized in refactoring Java code. Code refactoring is the process of improving the internal structure, readability, and
                    maintainability of a software codebase without altering its external behavior or functionality. You must output a refactored version of the code.
                    Don't return natural langiage explanations
                    """

            query = """
                unrefactored code snippet(java):: 
                {} 

                # refactored version of the same code snippet:
                """.format(java_code)
                
            llm_code = llm.query_llm(prompt, query, model=config.MODEL_NAME)
            llm_code = llm_code.replace("```java", "").replace("```", "")
            

            write_to_java_file(file_path=path_to_java_file_after, java_code=llm_code)

            #Write the improved code in the results file
            write_to_java_file(file_path=f"single_agent_results/results/{protject_name}/{target_class}/original_java_code.java", java_code=java_code)
            write_to_java_file(file_path=f"single_agent_results/results/{protject_name}/{target_class}/improved_java_code.java", java_code=llm_code)


            print("-------------------- Compile the improved code ---------------------------------------")

            project_directory = f"single_agent_results/projects_after/{protject_name}"
            is_compiled = compile_project_with_maven(project_directory)
            if is_compiled == False:
                results["Compilation"] = False
                results["Test passed"] = False
                results["is improved"] = False 
                write_to_java_file(file_path=path_to_java_file_after, java_code=java_code)
                export_dict_to_json(results, f"single_agent_results/results/{protject_name}/{target_class}/metrics")
                continue

            print("------------ Test the improved code ---------------------------------------")
            graph_path = f"data/graphs/{protject_name}/{target_class}_dependency_graph.json"
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
                        break
                
            write_to_java_file(file_path=path_to_java_file_after, java_code=java_code)
            export_dict_to_json(results, f"single_agent_results/results/{protject_name}/{target_class}/metrics")
        except:
            continue
            








        

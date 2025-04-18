import multiprocessing
import random

LOG_FILE = "app.log" 
RESULT_FILE = "results.txt"  
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_ERROR = "ERROR"


def log_message(level, message):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as log_file:  
            log_entry = f"[{level}] {message}\n"
            log_file.write(log_entry)
        if level == LOG_LEVEL_INFO:
            print(f"[INFO] {message}")  
        elif level == LOG_LEVEL_ERROR:
            print(f"[ERROR] {message}")
    except Exception as e:
        print(f"Ошибка при записи лога: {e}")

def generate_random_matrix(rows, cols):
    return [[random.randint(1, 10) for _ in range(cols)] for _ in range(rows)]

def multiply_rows(matrix_a, matrix_b, rows_range, result_queue):
    result = []
    for i in rows_range:
        row_result = []
        for j in range(len(matrix_b[0])):
            element = sum(matrix_a[i][k] * matrix_b[k][j] for k in range(len(matrix_b)))
            row_result.append(element)
        result.append((i, row_result)) 
    result_queue.put(result)

def save_results(results_queue, output_file):
    try:
        with open(output_file, 'a', encoding='utf-8') as f: 
            while True:
                result = results_queue.get()
                if result == "DONE": 
                    break
                if not result:
                    log_message(LOG_LEVEL_ERROR, "Получен пустой результат из очереди.")
                    continue
                for row_index, row_data in result:
                    f.write(f"Строка {row_index}: {row_data}\n")
                    log_message(LOG_LEVEL_INFO, f"Результат строки {row_index} сохранён в файл.") 
    except Exception as e:
        log_message(LOG_LEVEL_ERROR, f"Ошибка при сохранении результатов: {e}")


def main():
    try:
        rows_a = int(input("Введите количество строк для матрицы A: "))
        cols_a = int(input("Введите количество столбцов для матрицы A: "))
        rows_b = int(input("Введите количество строк для матрицы B: "))
        cols_b = int(input("Введите количество столбцов для матрицы B: "))
    except ValueError:
        log_message(LOG_LEVEL_ERROR, "Ошибка: Введены некорректные данные.")
        return
    
    if cols_a != rows_b:
        log_message(LOG_LEVEL_ERROR, "Ошибка: Количество столбцов матрицы A должно быть равно количеству строк матрицы B.")
        return

    matrix_a = generate_random_matrix(rows_a, cols_a)
    matrix_b = generate_random_matrix(rows_b, cols_b)

    log_message(LOG_LEVEL_INFO, "Матрица A:")
    for row in matrix_a:
        log_message(LOG_LEVEL_INFO, str(row))

    log_message(LOG_LEVEL_INFO, "Матрица B:")
    for row in matrix_b:
        log_message(LOG_LEVEL_INFO, str(row))

    cpu_count = multiprocessing.cpu_count()  
    max_processes = min(int(cpu_count * 0.75), rows_a)  
    log_message(LOG_LEVEL_INFO, f"У вашего процессора {cpu_count} потоков. Максимальное допустимое количество процессов: {max_processes}.")

    try:
        num_processes = int(input(f"Введите количество процессов (не более {max_processes}): "))
        if num_processes > max_processes or num_processes <= 0:
            log_message(LOG_LEVEL_ERROR, "Ошибка: Недопустимое количество процессов.")
            return
    except ValueError:
        log_message(LOG_LEVEL_ERROR, "Ошибка: Введено некорректное количество процессов.")
        return

    log_message(LOG_LEVEL_INFO, f"Используется {num_processes} процессов.")

    chunk_size = rows_a // num_processes
    processes = []
    result_queue = multiprocessing.Queue()

    for i in range(num_processes):
        start_row = i * chunk_size
        end_row = (i + 1) * chunk_size if i != num_processes - 1 else rows_a
        process = multiprocessing.Process(target=multiply_rows, args=(matrix_a, matrix_b, range(start_row, end_row), result_queue))
        processes.append(process)
        process.start()

    save_process = multiprocessing.Process(target=save_results, args=(result_queue, RESULT_FILE))
    save_process.start()

    for process in processes:
        process.join()

    result_queue.put("DONE")
    save_process.join()

    log_message(LOG_LEVEL_INFO, "Перемножение матриц завершено. Результаты сохранены в файл.")

if __name__ == "__main__":
    main()
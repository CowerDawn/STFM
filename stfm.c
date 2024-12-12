#include <ncurses.h>
#include <dirent.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <ctype.h>

#define MAX_FILENAME_LENGTH 256
#define MAX_FILES 1024
#define MAX_HISTORY 100
#define FILES_PER_PAGE 10

typedef struct {
    char name[MAX_FILENAME_LENGTH];
    int is_dir;
    int is_bash;
    int is_image;
    int is_text;
    int is_media;
} FileEntry;

FileEntry files[MAX_FILES];
int file_count = 0;
int current_index = 0;
char current_path[MAX_FILENAME_LENGTH] = ".";
char history[MAX_HISTORY][MAX_FILENAME_LENGTH];
int history_index = 0;
int current_page = 0;

void add_to_history(const char *path) {
    if (history_index < MAX_HISTORY) {
        strcpy(history[history_index], path);
        history_index++;
    }
}

void load_directory(const char *path) {
    DIR *dir;
    struct dirent *entry;
    struct stat file_stat;

    file_count = 0;
    strcpy(current_path, path);

    if ((dir = opendir(path)) == NULL) {
        perror("Unable to open directory");
        exit(EXIT_FAILURE);
    }

    while ((entry = readdir(dir)) != NULL && file_count < MAX_FILES) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        char full_path[MAX_FILENAME_LENGTH];
        snprintf(full_path, sizeof(full_path), "%s/%s", path, entry->d_name);

        if (stat(full_path, &file_stat) == 0) {
            files[file_count].is_dir = S_ISDIR(file_stat.st_mode);
            strncpy(files[file_count].name, entry->d_name, MAX_FILENAME_LENGTH);

            files[file_count].is_bash = (strstr(entry->d_name, ".sh") != NULL);

            const char *image_extensions[] = {".jpg", ".png", ".gif", ".bmp", ".jpeg"};
            files[file_count].is_image = 0;
            for (int i = 0; i < 5; i++) {
                if (strstr(entry->d_name, image_extensions[i]) != NULL) {
                    files[file_count].is_image = 1;
                    break;
                }
            }

            const char *text_extensions[] = {".txt", ".md", ".log", ".csv", ".ini", ".conf"};
            files[file_count].is_text = 0;
            for (int i = 0; i < 6; i++) {
                if (strstr(entry->d_name, text_extensions[i]) != NULL) {
                    files[file_count].is_text = 1;
                    break;
                }
            }

            const char *media_extensions[] = {".mp3", ".wav", ".mp4", ".avi", ".mkv", ".flac"};
            files[file_count].is_media = 0;
            for (int i = 0; i < 6; i++) {
                if (strstr(entry->d_name, media_extensions[i]) != NULL) {
                    files[file_count].is_media = 1;
                    break;
                }
            }

            file_count++;
        }
    }

    closedir(dir);
}

void draw_ui() {
    clear();
    int start_index = current_page * FILES_PER_PAGE;
    int end_index = start_index + FILES_PER_PAGE;
    if (end_index > file_count) {
        end_index = file_count;
    }

    for (int i = start_index; i < end_index; i++) {
        if (i == current_index) {
            attron(A_REVERSE);
        }
        if (files[i].is_dir) {
            attron(COLOR_PAIR(2));
            printw("[DIR] %s\n", files[i].name);
            attroff(COLOR_PAIR(2));
        } else if (files[i].is_bash) {
            attron(COLOR_PAIR(1));
            printw("      %s\n", files[i].name);
            attroff(COLOR_PAIR(1));
        } else if (files[i].is_image) {
            attron(COLOR_PAIR(3));
            printw("      %s\n", files[i].name);
            attroff(COLOR_PAIR(3));
        } else if (files[i].is_text) {
            attron(COLOR_PAIR(4));
            printw("      %s\n", files[i].name);
            attroff(COLOR_PAIR(4));
        } else if (files[i].is_media) {
            attron(COLOR_PAIR(5));
            printw("      %s\n", files[i].name);
            attroff(COLOR_PAIR(5));
        } else {
            printw("      %s\n", files[i].name);
        }
        if (i == current_index) {
            attroff(A_REVERSE);
        }
    }

    mvprintw(LINES - 1, 0, "Page %d/%d", current_page + 1, (file_count + FILES_PER_PAGE - 1) / FILES_PER_PAGE);
    refresh();
}

void open_file_with_default_app(const char *path) {
    pid_t pid = fork();
    if (pid == 0) {
        execlp("xdg-open", "xdg-open", path, NULL);
        exit(EXIT_FAILURE);
    } else if (pid < 0) {
        perror("Fork failed");
    }
}

void run_bash_file(const char *path) {
    pid_t pid = fork();
    if (pid == 0) {
        execlp("bash", "bash", path, NULL);
        exit(EXIT_FAILURE);
    } else if (pid < 0) {
        perror("Fork failed");
    }
}

void delete_file_or_directory() {
    char full_path[MAX_FILENAME_LENGTH];
    snprintf(full_path, sizeof(full_path), "%s/%s", current_path, files[current_index].name);

    mvprintw(LINES - 2, 0, "Are you sure you want to delete '%s'? (Y/N)", files[current_index].name);
    refresh();

    int ch = getch();
    if (toupper(ch) == 'Y') {
        if (files[current_index].is_dir) {
            if (rmdir(full_path) == 0) {
                mvprintw(LINES - 2, 0, "Directory '%s' deleted successfully.", files[current_index].name);
            } else {
                mvprintw(LINES - 2, 0, "Failed to delete directory '%s'.", files[current_index].name);
            }
        } else {
            if (unlink(full_path) == 0) {
                mvprintw(LINES - 2, 0, "File '%s' deleted successfully.", files[current_index].name);
            } else {
                mvprintw(LINES - 2, 0, "Failed to delete file '%s'.", files[current_index].name);
            }
        }
        refresh();
        usleep(1000000);
        load_directory(current_path);
    }
}

void create_directory() {
    char new_dir_name[MAX_FILENAME_LENGTH];
    mvprintw(LINES - 2, 0, "Enter name for new directory: ");
    refresh();
    echo();
    getnstr(new_dir_name, MAX_FILENAME_LENGTH);
    noecho();

    char full_path[MAX_FILENAME_LENGTH];
    snprintf(full_path, sizeof(full_path), "%s/%s", current_path, new_dir_name);

    if (mkdir(full_path, 0755) == 0) {
        mvprintw(LINES - 2, 0, "Directory '%s' created successfully.", new_dir_name);
        load_directory(current_path);
    } else {
        mvprintw(LINES - 2, 0, "Failed to create directory '%s'.", new_dir_name);
    }
    refresh();
    usleep(1000000);
}

void create_text_file() {
    char new_file_name[MAX_FILENAME_LENGTH];
    mvprintw(LINES - 2, 0, "Enter name for new text file: ");
    refresh();
    echo();
    getnstr(new_file_name, MAX_FILENAME_LENGTH);
    noecho();

    char full_path[MAX_FILENAME_LENGTH];
    snprintf(full_path, sizeof(full_path), "%s/%s", current_path, new_file_name);

    FILE *file = fopen(full_path, "w");
    if (file != NULL) {
        fclose(file);
        mvprintw(LINES - 2, 0, "Text file '%s' created successfully.", new_file_name);
        load_directory(current_path);
    } else {
        mvprintw(LINES - 2, 0, "Failed to create text file '%s'.", new_file_name);
    }
    refresh();
    usleep(1000000);
}

void handle_input() {
    int ch = getch();
    switch (ch) {
        case KEY_UP:
            if (current_index > 0) {
                current_index--;
                if (current_index < current_page * FILES_PER_PAGE) {
                    current_page--;
                }
            }
            break;
        case KEY_DOWN:
            if (current_index < file_count - 1) {
                current_index++;
                if (current_index >= (current_page + 1) * FILES_PER_PAGE) {
                    current_page++;
                }
            }
            break;
        case '\n':
        case KEY_RIGHT:
            if (files[current_index].is_dir) {
                char new_path[MAX_FILENAME_LENGTH];
                snprintf(new_path, sizeof(new_path), "%s/%s", current_path, files[current_index].name);
                add_to_history(current_path);
                load_directory(new_path);
                current_index = 0;
                current_page = 0;
            } else if (files[current_index].is_bash) {
                char full_path[MAX_FILENAME_LENGTH];
                snprintf(full_path, sizeof(full_path), "%s/%s", current_path, files[current_index].name);
                run_bash_file(full_path);
            } else {
                char full_path[MAX_FILENAME_LENGTH];
                snprintf(full_path, sizeof(full_path), "%s/%s", current_path, files[current_index].name);
                open_file_with_default_app(full_path);
            }
            break;
        case KEY_LEFT:
            if (strcmp(current_path, ".") != 0) {
                char *last_slash = strrchr(current_path, '/');
                if (last_slash != NULL) {
                    *last_slash = '\0';
                    if (strlen(current_path) == 0) {
                        strcpy(current_path, ".");
                    }
                    load_directory(current_path);
                    current_index = 0;
                    current_page = 0;
                }
            }
            break;
        case 'h':
            char *home_dir = getenv("HOME");
            if (home_dir != NULL) {
                load_directory(home_dir);
                current_index = 0;
                current_page = 0;
            }
            break;
        case 's':
            if (history_index > 0) {
                history_index--;
                load_directory(history[history_index]);
                current_index = 0;
                current_page = 0;
            }
            break;
        case 'q':
            endwin();
            exit(EXIT_SUCCESS);
            break;
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
            current_page = ch - '1';
            if (current_page * FILES_PER_PAGE >= file_count) {
                current_page = (file_count - 1) / FILES_PER_PAGE;
            }
            current_index = current_page * FILES_PER_PAGE;
            break;
        case 'A':
            delete_file_or_directory();
            break;
        case 'D':
            create_directory();
            break;
        case 'S':
            create_text_file();
            break;
    }
}

int main() {
    initscr();
    start_color();
    init_pair(1, COLOR_GREEN, COLOR_BLACK);
    init_pair(2, COLOR_BLUE, COLOR_BLACK);
    init_pair(3, COLOR_MAGENTA, COLOR_BLACK);
    init_pair(4, COLOR_GREEN, COLOR_BLACK);
    init_pair(5, COLOR_YELLOW, COLOR_BLACK);
    cbreak();
    noecho();
    keypad(stdscr, TRUE);

    load_directory(current_path);

    while (1) {
        draw_ui();
        handle_input();
    }

    endwin();
    return 0;
}

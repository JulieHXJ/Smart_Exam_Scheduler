import type { Exam, ExamFlag } from "./types";

export const ALL = "all";

export type Filters = {
  search: string;
  faculty: string;
  program: string;
  semester: string;
  spo: string;
  type: string;
  flag: typeof ALL | ExamFlag;
};

export const emptyFilters: Filters = {
  search: "",
  faculty: ALL,
  program: ALL,
  semester: ALL,
  spo: ALL,
  type: ALL,
  flag: ALL,
};

export function applyFilters(exams: Exam[], filters: Filters): Exam[] {
  const query = filters.search.trim().toLowerCase();
  return exams.filter(
    (exam) =>
      (!query ||
        exam.title.toLowerCase().includes(query) ||
        exam.examiner.toLowerCase().includes(query)) &&
      (filters.faculty === ALL || exam.faculty === filters.faculty) &&
      (filters.program === ALL || exam.program === filters.program) &&
      (filters.semester === ALL ||
        String(exam.semester) === filters.semester) &&
      (filters.spo === ALL || exam.spo === filters.spo) &&
      (filters.type === ALL || exam.type === filters.type) &&
      (filters.flag === ALL || exam.flags.includes(filters.flag)),
  );
}

export const unique = <T,>(values: T[]): T[] => [...new Set(values)];

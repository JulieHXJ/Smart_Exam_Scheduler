/** Program identifiers supported by exam planning. */
export type ProgramCode =
  | "IN"
  | "WI"
  | "TI"
  | "IIS"
  | "KIR"
  | "WPF Bachelor"
  | "WPF Master"
  | "ITPM"
  | "SE"
  | "IA";

/** Exam format values aligned with the backend ExamType. */
export type ExamType = "written" | "digital" | "oral" | "presentation";

/** User-facing labels for each exam format. */
export const EXAM_TYPE_LABEL: Record<ExamType, string> = {
  written: "Written exam",
  digital: "Digital exam",
  oral: "Oral exam",
  presentation: "Presentation",
};

/** Exam markers: locked date/room, digital format, repeater exam, or cross-program mapping. */
export type ExamFlag = "locked" | "digital" | "repeater" | "mapped";

/** Whether an exam is included in the term draft or needs review first. */
export type ExamStatus = "selected" | "review";

export type Exam = {
  id: string;
  title: string;
  program: ProgramCode;
  semester: number;
  /** Grouping label used in the exams table. */
  area: string;
  faculty: string;
  examiner: string;
  durationMinutes: number;
  estimatedStudents: number;
  /** Applicable study and examination regulations, such as "SPO 2024". */
  spo: string;
  type: ExamType;
  flags: ExamFlag[];
  status: ExamStatus;
};

export type RoomType = "classroom" | "lab";

export type BlockedTime = {
  /** Display text describing the blocked time or event. */
  label: string;
  /** Marks a fixed event, which is displayed with a lock icon. */
  fixedEvent?: boolean;
};

export type Room = {
  id: string;
  name: string;
  /** Building or group label used in the rooms table. */
  building: string;
  capacity: number;
  /** Allowed capacity overbooking as a percentage. */
  overbookingPercent: number;
  type: RoomType;
  blocked: BlockedTime[];
};

export type ExaminerPreference =
  | "Morning"
  | "Afternoon"
  | "Earlier dates"
  | "No preference";

export type Examiner = {
  id: string;
  name: string;
  examCount: number;
  /** Workload percentage; values above 100 exceed the limit. */
  workloadPercent: number;
  /** Availability or scheduling restriction, or "None" when unrestricted. */
  restriction: string;
  preference: ExaminerPreference;
};

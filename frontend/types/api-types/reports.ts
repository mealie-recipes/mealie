/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type ReportCategory = "backup" | "restore" | "migration";
export type ReportSummaryStatus = "in-progress" | "success" | "failure" | "partial";

export interface ReportCreate {
  timestamp?: string;
  category: ReportCategory;
  groupId: string;
  name: string;
  status?: ReportSummaryStatus & string;
}
export interface ReportEntryCreate {
  reportId: string;
  timestamp?: string;
  success?: boolean;
  message: string;
  exception?: string;
}
export interface ReportEntryOut {
  reportId: string;
  timestamp?: string;
  success?: boolean;
  message: string;
  exception?: string;
  id: string;
}
export interface ReportOut {
  timestamp?: string;
  category: ReportCategory;
  groupId: string;
  name: string;
  status?: ReportSummaryStatus & string;
  id: string;
  entries?: ReportEntryOut[];
}
export interface ReportSummary {
  timestamp?: string;
  category: ReportCategory;
  groupId: string;
  name: string;
  status?: ReportSummaryStatus & string;
  id: string;
}

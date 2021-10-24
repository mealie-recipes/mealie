export interface ServerTask {
  id: number;
  groupId: number;
  callback: string;
  createdAt: string;
  status: string;
  log: string;
}

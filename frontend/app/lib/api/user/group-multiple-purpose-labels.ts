import { BaseCRUDAPI } from "../base/base-clients";
import type { MultiPurposeLabelCreate, MultiPurposeLabelOut, MultiPurposeLabelUpdate } from "~/lib/api/types/labels";

const prefix = "/api";

const routes = {
  labels: `${prefix}/groups/labels`,
  labelsId: (id: string | number) => `${prefix}/groups/labels/${id}`,
  labelsEmpty: `${prefix}/groups/labels/empty`,
  labelsMerge: `${prefix}/groups/labels/merge`,
};

export class MultiPurposeLabelsApi extends BaseCRUDAPI<
  MultiPurposeLabelCreate,
  MultiPurposeLabelOut,
  MultiPurposeLabelUpdate
> {
  baseRoute = routes.labels;
  itemRoute = routes.labelsId;

  async getEmpty() {
    return await this.requests.get<MultiPurposeLabelOut[]>(routes.labelsEmpty);
  }

  merge(fromId: string, toId: string) {
    return this.requests.post<MultiPurposeLabelOut>(routes.labelsMerge, { fromId, toId });
  }
}

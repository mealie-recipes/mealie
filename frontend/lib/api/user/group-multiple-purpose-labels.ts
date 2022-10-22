import { BaseCRUDAPI } from "../base/base-clients";
import { MultiPurposeLabelCreate, MultiPurposeLabelOut, MultiPurposeLabelUpdate } from "~/lib/api/types/labels";

const prefix = "/api";

const routes = {
  labels: `${prefix}/groups/labels`,
  labelsId: (id: string | number) => `${prefix}/groups/labels/${id}`,
};

export class MultiPurposeLabelsApi extends BaseCRUDAPI<
  MultiPurposeLabelCreate,
  MultiPurposeLabelOut,
  MultiPurposeLabelUpdate
> {
  baseRoute = routes.labels;
  itemRoute = routes.labelsId;
}

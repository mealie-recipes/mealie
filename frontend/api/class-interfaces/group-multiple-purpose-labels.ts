import { BaseCRUDAPI } from "../_base";
import { MultiPurposeLabelCreate, MultiPurposeLabelOut } from "~/types/api-types/labels";

const prefix = "/api";

const routes = {
  labels: `${prefix}/groups/labels`,
  labelsId: (id: string | number) => `${prefix}/groups/labels/${id}`,
};

export class MultiPurposeLabelsApi extends BaseCRUDAPI<MultiPurposeLabelOut, MultiPurposeLabelCreate> {
  baseRoute = routes.labels;
  itemRoute = routes.labelsId;
}

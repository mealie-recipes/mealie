import { BaseCRUDAPI } from "../_base";

const prefix = "/api";

const routes = {
  labels: `${prefix}/groups/labels`,
  labelsId: (id: string | number) => `${prefix}/groups/labels/${id}`,
};

export interface CreateLabel {
  name: string;
}

export interface Label extends CreateLabel {
  id: string;
  groupId: string;
}

export class MultiPurposeLabelsApi extends BaseCRUDAPI<Label, CreateLabel> {
  baseRoute = routes.labels;
  itemRoute = routes.labelsId;
}

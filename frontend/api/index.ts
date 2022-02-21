import { RecipeAPI } from "./class-interfaces/recipes";
import { UserApi } from "./class-interfaces/users";
import { GroupAPI } from "./class-interfaces/groups";
import { BackupAPI } from "./class-interfaces/backups";
import { UploadFile } from "./class-interfaces/upload";
import { CategoriesAPI } from "./class-interfaces/organizer-categories";
import { TagsAPI } from "./class-interfaces/organizer-tags";
import { UtilsAPI } from "./class-interfaces/utils";
import { FoodAPI } from "./class-interfaces/recipe-foods";
import { UnitAPI } from "./class-interfaces/recipe-units";
import { CookbookAPI } from "./class-interfaces/group-cookbooks";
import { WebhooksAPI } from "./class-interfaces/group-webhooks";
import { RegisterAPI } from "./class-interfaces/user-registration";
import { MealPlanAPI } from "./class-interfaces/group-mealplan";
import { EmailAPI } from "./class-interfaces/email";
import { BulkActionsAPI } from "./class-interfaces/recipe-bulk-actions";
import { GroupServerTaskAPI } from "./class-interfaces/group-tasks";
import { AdminAPI } from "./admin-api";
import { ToolsApi } from "./class-interfaces/organizer-tools";
import { GroupMigrationApi } from "./class-interfaces/group-migrations";
import { GroupReportsApi } from "./class-interfaces/group-reports";
import { ShoppingApi } from "./class-interfaces/group-shopping-lists";
import { MultiPurposeLabelsApi } from "./class-interfaces/group-multiple-purpose-labels";
import { GroupEventNotifierApi } from "./class-interfaces/group-event-notifier";
import { MealPlanRulesApi } from "./class-interfaces/group-mealplan-rules";
import { ApiRequestInstance } from "~/types/api";

class Api {
  public recipes: RecipeAPI;
  public users: UserApi;
  public groups: GroupAPI;
  public backups: BackupAPI;
  public categories: CategoriesAPI;
  public tags: TagsAPI;
  public utils: UtilsAPI;
  public foods: FoodAPI;
  public units: UnitAPI;
  public cookbooks: CookbookAPI;
  public groupWebhooks: WebhooksAPI;
  public register: RegisterAPI;
  public mealplans: MealPlanAPI;
  public mealplanRules: MealPlanRulesApi;
  public email: EmailAPI;
  public bulk: BulkActionsAPI;
  public groupMigration: GroupMigrationApi;
  public groupReports: GroupReportsApi;
  public grouperServerTasks: GroupServerTaskAPI;
  public tools: ToolsApi;
  public shopping: ShoppingApi;
  public multiPurposeLabels: MultiPurposeLabelsApi;
  public groupEventNotifier: GroupEventNotifierApi;
  public upload: UploadFile;

  constructor(requests: ApiRequestInstance) {
    // Recipes
    this.recipes = new RecipeAPI(requests);
    this.categories = new CategoriesAPI(requests);
    this.tags = new TagsAPI(requests);
    this.units = new UnitAPI(requests);
    this.foods = new FoodAPI(requests);
    this.tools = new ToolsApi(requests);

    // Users
    this.users = new UserApi(requests);
    this.groups = new GroupAPI(requests);
    this.cookbooks = new CookbookAPI(requests);
    this.groupWebhooks = new WebhooksAPI(requests);
    this.register = new RegisterAPI(requests);
    this.mealplans = new MealPlanAPI(requests);
    this.mealplanRules = new MealPlanRulesApi(requests);
    this.grouperServerTasks = new GroupServerTaskAPI(requests);

    // Group
    this.groupMigration = new GroupMigrationApi(requests);
    this.groupReports = new GroupReportsApi(requests);
    this.shopping = new ShoppingApi(requests);
    this.multiPurposeLabels = new MultiPurposeLabelsApi(requests);

    // Admin
    this.backups = new BackupAPI(requests);

    // Utils
    this.upload = new UploadFile(requests);
    this.utils = new UtilsAPI(requests);

    this.email = new EmailAPI(requests);
    this.bulk = new BulkActionsAPI(requests);
    this.groupEventNotifier = new GroupEventNotifierApi(requests);

    Object.freeze(this);
  }
}

export { Api, AdminAPI };

import { RecipeAPI } from "./user/recipes";
import { UserApi } from "./user/users";
import { HouseholdAPI } from "./user/households";
import { GroupAPI } from "./user/groups";
import { BackupAPI } from "./user/backups";
import { UploadFile } from "./user/upload";
import { CategoriesAPI } from "./user/organizer-categories";
import { TagsAPI } from "./user/organizer-tags";
import { UtilsAPI } from "./user/utils";
import { FoodAPI } from "./user/recipe-foods";
import { UnitAPI } from "./user/recipe-units";
import { CookbookAPI } from "./user/group-cookbooks";
import { GroupRecipeActionsAPI } from "./user/group-recipe-actions";
import { WebhooksAPI } from "./user/group-webhooks";
import { RegisterAPI } from "./user/user-registration";
import { MealPlanAPI } from "./user/group-mealplan";
import { EmailAPI } from "./user/email";
import { BulkActionsAPI } from "./user/recipe-bulk-actions";
import { ToolsApi } from "./user/organizer-tools";
import { GroupMigrationApi } from "./user/group-migrations";
import { GroupReportsApi } from "./user/group-reports";
import { ShoppingApi } from "./user/group-shopping-lists";
import { MultiPurposeLabelsApi } from "./user/group-multiple-purpose-labels";
import { GroupEventNotifierApi } from "./user/group-event-notifier";
import { MealPlanRulesApi } from "./user/group-mealplan-rules";
import { GroupDataSeederApi } from "./user/group-seeder";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";

export class UserApiClient {
  public recipes: RecipeAPI;
  public users: UserApi;
  public households: HouseholdAPI;
  public groups: GroupAPI;
  public backups: BackupAPI;
  public categories: CategoriesAPI;
  public tags: TagsAPI;
  public utils: UtilsAPI;
  public foods: FoodAPI;
  public units: UnitAPI;
  public cookbooks: CookbookAPI;
  public groupRecipeActions: GroupRecipeActionsAPI;
  public groupWebhooks: WebhooksAPI;
  public register: RegisterAPI;
  public mealplans: MealPlanAPI;
  public mealplanRules: MealPlanRulesApi;
  public email: EmailAPI;
  public bulk: BulkActionsAPI;
  public groupMigration: GroupMigrationApi;
  public groupReports: GroupReportsApi;
  public tools: ToolsApi;
  public shopping: ShoppingApi;
  public multiPurposeLabels: MultiPurposeLabelsApi;
  public groupEventNotifier: GroupEventNotifierApi;
  public upload: UploadFile;
  public seeders: GroupDataSeederApi;

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
    this.households = new HouseholdAPI(requests);
    this.groups = new GroupAPI(requests);
    this.cookbooks = new CookbookAPI(requests);
    this.groupRecipeActions = new GroupRecipeActionsAPI(requests);
    this.groupWebhooks = new WebhooksAPI(requests);
    this.register = new RegisterAPI(requests);
    this.mealplans = new MealPlanAPI(requests);
    this.mealplanRules = new MealPlanRulesApi(requests);

    // Group
    this.groupMigration = new GroupMigrationApi(requests);
    this.groupReports = new GroupReportsApi(requests);
    this.shopping = new ShoppingApi(requests);
    this.multiPurposeLabels = new MultiPurposeLabelsApi(requests);
    this.seeders = new GroupDataSeederApi(requests);

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

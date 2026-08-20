import Mainers from "./pages/Mainers.svelte";
import Dashboard from "./pages/Dashboard.svelte";
import Wallet from "./pages/Wallet.svelte";
import Lottery from "./pages/Lottery.svelte";
import Brand from "./pages/Brand.svelte";
import AppStore from "./pages/AppStore.svelte";
import Marketplace from "./pages/Marketplace.svelte";
import NotFound from "./pages/NotFound.svelte";

export const routes = {
  "/": Mainers,
  "/dashboard": Dashboard,
  "/wallet": Wallet,
  "/marketplace": Marketplace,
  "/lottery": Lottery,
  "/brand": Brand,
  "/store": AppStore,
  "*": NotFound,
};

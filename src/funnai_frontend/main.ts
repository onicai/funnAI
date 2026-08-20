import { mount } from "svelte";
import App from "./App.svelte";
import "./app.css";
import { startAppVersionPolling } from "./helpers/appVersion";

const target = document.getElementById("root");
if (!target) {
  throw new Error("Missing #root element");
}

const app = mount(App, { target });

startAppVersionPolling();

export default app;

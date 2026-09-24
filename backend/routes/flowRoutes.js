import express from "express";
import { getLatestFlows } from "../controllers/flowController.js";


const router = express.Router();
router.get("/latest-flows",getLatestFlows);
export default router;